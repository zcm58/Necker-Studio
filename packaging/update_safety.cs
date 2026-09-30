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
        for (string part = full; !String.IsNullOrEmpty(part); part = Path.GetDirectoryName(part))
        {
            try
            {
                FileAttributes attributes = File.GetAttributes(part);
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Linked update paths are not supported.");
            }
            catch (FileNotFoundException) { }
            catch (DirectoryNotFoundException) { }
        }
    }

    public static FileStream OpenRead(string path)
    {
        CheckPath(path);
        var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        FileInfo info;
        if (!GetFileInformationByHandle(stream.SafeFileHandle, out info) || info.Links != 1 || (info.Attributes & 0x400) != 0)
        {
            stream.Dispose();
            throw new IOException("Update files must be regular files with one link.");
        }
        return stream;
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
