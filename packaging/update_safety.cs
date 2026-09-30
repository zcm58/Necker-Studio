using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Microsoft.Win32;
using Microsoft.Win32.SafeHandles;

internal static class Safety
{
    [StructLayout(LayoutKind.Sequential)]
    private struct FileInfo
    {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME Creation, Access, Write;
        public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }
    [DllImport("kernel32.dll", SetLastError=true)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out FileInfo info);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern SafeFileHandle CreateFile(string path, uint access, uint share,
        IntPtr security, uint disposition, uint flags, IntPtr template);
    // Keep each checked ancestor pinned for this short-lived verifier/helper process.
    // Denying delete sharing prevents it being replaced by a junction after checking.
    private static readonly Dictionary<string, SafeFileHandle> Directories =
        new Dictionary<string, SafeFileHandle>(StringComparer.OrdinalIgnoreCase);

    private static void PinDirectory(string path)
    {
        if (String.IsNullOrEmpty(path) || Directories.ContainsKey(path)) return;
        PinDirectory(Path.GetDirectoryName(path));
        if (!Directory.Exists(path))
        {
            if (File.Exists(path)) throw new IOException("An update directory is occupied by a file.");
            return; // A new full-install directory may not exist yet.
        }
        var handle = CreateFile(path, 0x80, 3, IntPtr.Zero, 3, 0x02200000, IntPtr.Zero);
        FileInfo info;
        if (handle.IsInvalid || !GetFileInformationByHandle(handle, out info) ||
            (info.Attributes & 0x400) != 0 || (info.Attributes & 0x10) == 0)
        {
            handle.Dispose();
            throw new IOException("An update directory is linked or cannot be pinned.");
        }
        Directories.Add(path, handle);
    }

    public static string Root(string path)
    {
        string root = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar);
        if (!Path.IsPathRooted(path) || root.StartsWith(@"\\") || root.Length < 10 ||
            root == Path.GetPathRoot(root).TrimEnd('\\') ||
            String.Equals(root, Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), StringComparison.OrdinalIgnoreCase))
            throw new IOException("Unsafe installation directory.");
        CheckPath(root);
        if (Directory.Exists(Path.Combine(root, ".git"))) throw new IOException("A source checkout cannot be updated by setup.");
        return root;
    }

    public static void CheckPath(string path)
    {
        string full = Path.GetFullPath(path);
        PinDirectory(Path.GetDirectoryName(full));
        try
        {
            FileAttributes attributes = File.GetAttributes(full);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new IOException("Linked update paths are not supported.");
            if ((attributes & FileAttributes.Directory) != 0) PinDirectory(full);
        }
        catch (FileNotFoundException) { }
        catch (DirectoryNotFoundException) { }
    }

    public static FileStream OpenRead(string path)
    {
        PinDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
        var handle = CreateFile(path, 0x80000000, 1, IntPtr.Zero, 3, 0x08200000, IntPtr.Zero);
        FileInfo info;
        if (handle.IsInvalid || !GetFileInformationByHandle(handle, out info) || info.Links != 1 || (info.Attributes & 0x410) != 0)
        {
            handle.Dispose();
            throw new IOException("Update files must be regular files with one link.");
        }
        return new FileStream(handle, FileAccess.Read, 65536);
    }

    public static string Hash(Stream stream)
    {
        stream.Position = 0;
        using (var sha = SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }

    public static string Hash(string path)
    {
        using (var stream = OpenRead(path)) return Hash(stream);
    }

    public static string Quote(string value)
    {
        if (value.IndexOfAny(new[] {'"', '\r', '\n', '\0'}) >= 0) throw new IOException("Invalid update argument.");
        return "\"" + value.TrimEnd('\\') + "\"";
    }

    public static string RegisteredVersion(string guid, string root)
    {
        using (var user = RegistryKey.OpenBaseKey(RegistryHive.CurrentUser, RegistryView.Registry64))
        using (var key = user.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\" + guid + "_is1"))
        {
            if (key == null || !String.Equals(Root((string)key.GetValue("InstallLocation", "")), root, StringComparison.OrdinalIgnoreCase))
                throw new IOException("The registered installation does not match this update.");
            return (string)key.GetValue("DisplayVersion", "");
        }
    }
}
