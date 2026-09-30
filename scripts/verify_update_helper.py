"""Exercise the native helper handshake, close/wait/install/restart in isolation."""
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import winreg

from build_patch import prepare, digest

PROJECT = Path(__file__).resolve().parents[1]
CSC = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
ISCC = Path(os.environ['LOCALAPPDATA']) / 'Programs/Inno/ISCC.exe'


def main():
    root = PROJECT / 'build' / ('helper-acceptance-' + uuid.uuid4().hex[:10])
    root.mkdir(parents=True)
    cache = root / 'cache'; cache.mkdir()
    guid = str(uuid.uuid4()).upper()
    keyname = rf'Software\Microsoft\Windows\CurrentVersion\Uninstall\{{{guid}}}_is1'
    installed = root / 'installed application'
    verifier = root / 'NeckerSetupVerifier.exe'
    subprocess.run([str(CSC),'/nologo','/target:exe','/platform:x64','/reference:System.Web.Extensions.dll',
        f'/out:{verifier}',str(PROJECT/'packaging/update_safety.cs'),str(PROJECT/'packaging/setup_verifier.cs')],check=True)
    helper_source = root / 'helper.cs'
    helper_source.write_text((PROJECT/'packaging/updater.cs').read_text().replace(
        '{5FC7235D-8D03-4668-9F37-508A1B481689}', '{'+guid+'}').replace(
        'Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "NicholasNiceNeckerCubeExperiment", "updates")',
        '@"' + str(cache) + '"'))
    helper = cache / 'test-helper.exe'
    subprocess.run([str(CSC),'/nologo','/target:exe','/platform:x64','/reference:System.Windows.Forms.dll',
        f'/out:{helper}',str(PROJECT/'packaging/update_safety.cs'),str(helper_source)],check=True)
    launcher_source = root / 'launcher.cs'
    launcher_source.write_text('using System; using System.IO; class Entry { static void Main() { File.WriteAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory,"restarted.txt"), "restarted"); } }')
    launcher = root / 'launcher.exe'
    subprocess.run([str(CSC),'/nologo','/target:exe',f'/out:{launcher}',str(launcher_source)],check=True)
    parent_source = root / 'parent.cs'
    parent_source.write_text(r'''using System; using System.IO; using System.Diagnostics;
class Entry {
static string Q(string value) { return "\"" + value + "\""; }
static int Main(string[] a) {
var start = new ProcessStartInfo(a[0], Process.GetCurrentProcess().Id + " " + Q(a[1]) + " 1.1 1.2 " + Q(a[2]) + " " + a[3] + " " + a[4]);
start.UseShellExecute=false; start.RedirectStandardInput=true; start.RedirectStandardOutput=true; start.CreateNoWindow=true;
using (var helper=Process.Start(start)) {
 if (helper.StandardOutput.ReadLine() != "READY") return 10;
 if (a[5] == "cancel") { helper.StandardInput.Close(); if (!helper.WaitForExit(10000)) return 11; return helper.ExitCode == 2 ? 0 : 12; }
 helper.StandardInput.WriteLine("ACCEPT"); helper.StandardInput.Flush();
 if (helper.StandardOutput.ReadLine() != "ACCEPTED") return 13;
 helper.StandardInput.Close();
 // Only after the acknowledgement does the app exit; helper owns the rest.
 return 0;
}
} }''')
    parent = root / 'parent.exe'
    subprocess.run([str(CSC),'/nologo','/target:exe',f'/out:{parent}',str(parent_source)],check=True)
    folders = []
    for version in ('1.1','1.2'):
        folder = root / ('bundle-'+version); (folder/'app').mkdir(parents=True); (folder/'runtime').mkdir()
        (folder/'app/release.json').write_text(json.dumps({'version':version}))
        (folder/'app/main.py').write_text(version)
        (folder/'NeckerExperiment.exe').write_bytes(launcher.read_bytes())
        (folder/'runtime/python.exe').write_bytes(parent.read_bytes())
        (folder/'manifest.json').write_text(json.dumps({p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}))
        folders.append(folder)
    source,target=folders
    dist=root/'dist'; dist.mkdir()
    for version,folder,patch_mode in [('1.1',source,False),('1.2',target,True)]:
        build=root/('build-'+version)
        prepare(folder,build,source/'manifest.json' if patch_mode else None,digest(source/'manifest.json') if patch_mode else None,'1.1' if patch_mode else None)
        args=[str(ISCC),'/Qp',f'/DAppVersion={version}',f'/DAppIdGuid={guid}',f'/DBundleRoot={folder}',f'/DInstallerOutput={dist}',
              f'/DPayloadList={build/"payload.iss"}',f'/DVerifierExe={verifier}']
        if patch_mode: args += ['/DPatchFromVersion=1.1',f'/DSourceManifest={source/"manifest.json"}']
        with (root/('compile-'+version+'.log')).open('w') as log:
            subprocess.run(args+[str(PROJECT/'packaging/necker.iss')],check=True,stdout=log,stderr=subprocess.STDOUT)
    setup=dist/'Nicholas-Nice-Necker-Cube-Experiment-Setup-1.1-x64.exe'
    subprocess.run([str(setup),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-','/NOICONS','/NOSHORTCUTS=1','/NOLAUNCH=1',f'/DIR={installed}'],check=True,timeout=60)
    patch=dist/'Nicholas-Nice-Necker-Cube-Experiment-Patch-1.1-to-1.2-x64.exe'
    sha=digest(patch); payload=cache/f'download-{sha}.exe'; payload.write_bytes(patch.read_bytes())
    parent_args=[str(installed/'runtime/python.exe'),str(helper),str(installed),str(payload),sha,str(payload.stat().st_size)]
    subprocess.run(parent_args+['cancel'],check=True,timeout=30)
    assert json.loads((installed/'app/release.json').read_text())['version']=='1.1'
    assert not (installed/'restarted.txt').exists()
    subprocess.run(parent_args+['accept'],check=True,timeout=30)
    deadline=time.monotonic()+60
    while not (installed/'restarted.txt').exists():
        if time.monotonic()>deadline: raise RuntimeError('Helper failed to install/restart in time; inspect the isolated fixture.')
        time.sleep(.1)
    assert json.loads((installed/'app/release.json').read_text())['version']=='1.2'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
        assert Path(winreg.QueryValueEx(key,'InstallLocation')[0]).resolve()==installed.resolve()
        assert winreg.QueryValueEx(key,'DisplayVersion')[0]=='1.2'
        uninstaller=Path(winreg.QueryValueEx(key,'UninstallString')[0].strip('"'))
    assert uninstaller.resolve().parent==installed.resolve()
    subprocess.run([str(uninstaller),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],check=True,timeout=60)
    report={'passed':True,'cancel_before_acceptance_preserves_installation':True,'accepted_install_waited_for_parent_exit':True,
            'patch_applied':True,'registration_verified':True,'restarted_after_success':True,'fixture_uninstalled':True}
    (root/'report.json').write_text(json.dumps(report,indent=2))
    print(root/'report.json',flush=True)


if __name__=='__main__': main()
