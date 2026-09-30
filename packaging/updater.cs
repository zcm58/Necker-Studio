using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

internal static class Updater
{
    private const string Guid = "{5FC7235D-8D03-4668-9F37-508A1B481689}";
    private const string Title = "Experiment update";

    [STAThread]
    private static int Main(string[] args)
    {
        bool accepted = false;
        try
        {
            if (args.Length != 7) throw new IOException("Invalid updater request.");
            string root = Safety.Root(args[1]);
            string oldVersion = args[2], newVersion = args[3];
            if (!Regex.IsMatch(oldVersion, @"^\d+\.\d+(\.\d+)?$") ||
                !Regex.IsMatch(newVersion, @"^\d+\.\d+(\.\d+)?$") ||
                new Version(newVersion).CompareTo(new Version(oldVersion)) <= 0)
                throw new IOException("The update must be newer than this installation.");
            string installer = Path.GetFullPath(args[4]);
            string cache = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "NicholasNiceNeckerCubeExperiment", "updates");
            string digest = args[5];
            if (!Regex.IsMatch(digest, "^[0-9a-f]{64}$") ||
                !String.Equals(installer, Path.Combine(cache, "download-" + digest + ".exe"), StringComparison.OrdinalIgnoreCase))
                throw new IOException("Invalid cached installer.");
            Safety.CheckPath(cache);
            string lockPath = Path.Combine(cache, "update.lock");
            Safety.CheckPath(lockPath);
            using (var cacheLock = new FileStream(lockPath, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.ReadWrite))
            {
                cacheLock.Lock(0, 1);
                using (var payload = Safety.OpenRead(installer))
                using (var parent = Process.GetProcessById(Int32.Parse(args[0], CultureInfo.InvariantCulture)))
                {
                    if (!String.Equals(Path.GetDirectoryName(parent.MainModule.FileName), Path.Combine(root, "runtime"), StringComparison.OrdinalIgnoreCase))
                        throw new IOException("The update request did not come from the installed application.");
                    if (payload.Length != Int64.Parse(args[6], CultureInfo.InvariantCulture) || Safety.Hash(payload) != digest ||
                        Safety.RegisteredVersion(Guid, root) != oldVersion)
                        throw new IOException("The update changed or no longer matches this installation.");
                    Console.WriteLine("READY");
                    Console.Out.Flush();
                    var input = Task.Factory.StartNew(() => Console.ReadLine());
                    if (!input.Wait(30000) || input.Result != "ACCEPT") return 2;
                    accepted = true;
                    Console.WriteLine("ACCEPTED");
                    Console.Out.Flush();
                    // A pinned Process object prevents PID reuse. Never force-close the app.
                    if (!parent.WaitForExit(120000)) throw new IOException("The application did not close. The update was not started.");
                    if (Safety.RegisteredVersion(Guid, root) != oldVersion)
                        throw new IOException("Another installer changed the application. Check for updates again.");
                    var start = new ProcessStartInfo(installer,
                        "/SILENT /SP- /NORESTART /SUPPRESSMSGBOXES /NOCLOSEAPPLICATIONS /NOLAUNCH=1 /DIR=" + Safety.Quote(root) +
                        " /LOG=" + Safety.Quote(Path.Combine(cache, "last-install.log")));
                    start.UseShellExecute = false;
                    start.WorkingDirectory = cache;
                    using (var setup = Process.Start(start))
                    {
                        setup.WaitForExit();
                        if (setup.ExitCode != 0)
                            throw new IOException("Installation did not complete (code " + setup.ExitCode + "). Use the full installer from GitHub Releases to repair the application.\n\nLog: " + Path.Combine(cache, "last-install.log"));
                    }
                    if (Safety.RegisteredVersion(Guid, root) != newVersion)
                        throw new IOException("Installation did not report the expected version. Use the full installer to repair it.");
                }
                // Keep the cache lock through verification and relaunch.
                Process.Start(new ProcessStartInfo(Path.Combine(root, "NeckerExperiment.exe"))
                    {UseShellExecute = false, WorkingDirectory = root});
            }
            return 0;
        }
        catch (Exception error)
        {
            if (accepted) MessageBox.Show(error.Message, Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            else { Console.WriteLine("ERROR"); Console.Out.Flush(); }
            return 1;
        }
    }
}
