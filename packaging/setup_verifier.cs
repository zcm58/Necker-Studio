using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;

// Runs from Inno's private temp directory, with no dependency on installed Python.
internal static class SetupVerifier
{
    private const string Marker = "necker-patch-pending.txt";

    private static Dictionary<string, string> Manifest(string path)
    {
        var serializer = new JavaScriptSerializer {MaxJsonLength = 16 * 1024 * 1024};
        using (var stream = Safety.OpenRead(path))
        using (var reader = new StreamReader(stream, Encoding.UTF8, true))
        {
            var records = serializer.Deserialize<Dictionary<string, string>>(reader.ReadToEnd());
            if (records == null || records.Count == 0 || records.Count > 100000) throw new IOException("Invalid inventory.");
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var record in records)
            {
                var parts = record.Key.Split('/');
                if (parts.Length == 0 || (parts[0] != "app" && parts[0] != "runtime" && parts[0] != "licenses" &&
                    record.Key != "NeckerExperiment.exe" && record.Key != "NeckerUpdater.exe"))
                    throw new IOException("Unknown inventory root.");
                foreach (var part in parts)
                    if (String.IsNullOrEmpty(part) || part == "." || part == ".." || part.EndsWith(".") || part.EndsWith(" ") ||
                        part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || Regex.IsMatch(part, @"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\.|$)", RegexOptions.IgnoreCase))
                        throw new IOException("Unsafe inventory path.");
                if (!names.Add(record.Key) || !Regex.IsMatch(record.Value, "^[0-9a-f]{64}$")) throw new IOException("Invalid inventory record.");
            }
            return records;
        }
    }

    private static string Target(string root, string relative)
    {
        string path = Path.Combine(root, relative.Replace('/', '\\'));
        Safety.CheckPath(path);
        return path;
    }

    private static bool Has(string path) { return File.Exists(path) || Directory.Exists(path); }

    private static void Verify(string root, Dictionary<string, string> records)
    {
        foreach (var record in records)
            if (Safety.Hash(Target(root, record.Key)) != record.Value)
                throw new IOException("File verification failed: " + record.Key);
    }

    private static int Main(string[] args)
    {
        try
        {
            // mode, root, source manifest or -, target manifest, from, to, GUID
            if (args.Length != 7) throw new IOException("Invalid setup verification request.");
            string root = Safety.Root(args[1]);
            var target = Manifest(args[3]);
            string marker = Target(root, Marker);
            string fingerprint = "NECKER-PATCH-1\n" + args[4] + "\n" + args[5] + "\n" +
                (args[2] == "-" ? "full" : Safety.Hash(args[2])) + "\n" + Safety.Hash(args[3]);
            if (args[0] == "prepare")
            {
                // Inspect existing destinations before any copy, including full repairs.
                foreach (var record in target)
                {
                    string destination = Target(root, record.Key);
                    if (Has(destination)) using (Safety.OpenRead(destination)) { }
                }
                string installedManifest = Target(root, "manifest.json");
                if (Has(installedManifest)) using (Safety.OpenRead(installedManifest)) { }
                if (args[2] == "-") return 0;
                var source = Manifest(args[2]);
                string registered = Safety.RegisteredVersion(args[6], root);
                bool recovery = Has(marker);
                if (recovery)
                {
                    using (var stream = Safety.OpenRead(marker))
                    using (var reader = new StreamReader(stream))
                        if (reader.ReadToEnd() != fingerprint) throw new IOException("Another patch is pending. Use the full installer.");
                    if (registered != args[4] && registered != args[5]) throw new IOException("Patch version mismatch.");
                    if (Has(installedManifest))
                    {
                        string hash = Safety.Hash(installedManifest);
                        if (hash != Safety.Hash(args[2]) && hash != Safety.Hash(args[3])) throw new IOException("Unknown installed inventory.");
                    }
                }
                else
                {
                    if (registered != args[4] || Safety.Hash(installedManifest) != Safety.Hash(args[2]))
                        throw new IOException("This patch requires the exact source version. Use the full installer.");
                }
                foreach (var record in source)
                {
                    if (!target.ContainsKey(record.Key)) throw new IOException("Removing files requires a full installer.");
                    string path = Target(root, record.Key);
                    bool changed = target[record.Key] != record.Value;
                    if (!Has(path) && recovery && changed) continue;
                    string hash = Safety.Hash(path);
                    if (hash != record.Value && !(recovery && changed && hash == target[record.Key]))
                        throw new IOException("The installed baseline has changed. Use the full installer to repair it.");
                }
                foreach (var record in target)
                {
                    string path = Target(root, record.Key);
                    if (!source.ContainsKey(record.Key) && Has(path) && (!recovery || Safety.Hash(path) != record.Value))
                        throw new IOException("A new application path is occupied. Use the full installer after moving that file.");
                }
                if (!recovery)
                {
                    byte[] data = Encoding.UTF8.GetBytes(fingerprint);
                    using (var file = new FileStream(marker, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                    { file.Write(data, 0, data.Length); file.Flush(true); }
                }
            }
            else if (args[0] == "finish")
            {
                Verify(root, target);
                if (Safety.Hash(Target(root, "manifest.json")) != Safety.Hash(args[3])) throw new IOException("Installed inventory verification failed.");
                if (Has(marker))
                {
                    string content;
                    using (var stream = Safety.OpenRead(marker))
                    using (var reader = new StreamReader(stream)) content = reader.ReadToEnd();
                    if (args[2] != "-" && content != fingerprint)
                        throw new IOException("Patch recovery identity changed.");
                    // A full repair removes only a recognized app recovery marker.
                    if (content.StartsWith("NECKER-PATCH-1\n", StringComparison.Ordinal)) File.Delete(marker);
                }
            }
            else throw new IOException("Unknown verification stage.");
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.Message);
            return 12;
        }
    }
}
