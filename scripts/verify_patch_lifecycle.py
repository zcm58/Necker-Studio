"""Native Inno lifecycle acceptance using a unique, disposable installation ID.

No production registration, cache, shortcuts, experiment or COM port is touched.
The fixture directory is retained as inspectable evidence, not recursively removed.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import winreg

from build_patch import prepare, digest

PROJECT = Path(__file__).resolve().parents[1]
CSC = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')
ISCC = Path(os.environ['LOCALAPPDATA']) / 'Programs/Inno/ISCC.exe'


def main():
    root = PROJECT / 'build' / ('patch-acceptance-' + uuid.uuid4().hex[:10])
    root.mkdir(parents=True)
    guid = str(uuid.uuid4()).upper()
    keyname = rf'Software\Microsoft\Windows\CurrentVersion\Uninstall\{{{guid}}}_is1'
    installed = root / 'installed application'
    verifier = root / 'NeckerSetupVerifier.exe'
    subprocess.run([str(CSC), '/nologo', '/target:exe', '/platform:x64',
                    '/reference:System.Web.Extensions.dll', f'/out:{verifier}',
                    str(PROJECT / 'packaging/update_safety.cs'), str(PROJECT / 'packaging/setup_verifier.cs')], check=True)
    subprocess.run([str(CSC), '/nologo', '/target:exe', '/platform:x64',
                    '/reference:System.Windows.Forms.dll', f'/out:{root / "NeckerUpdater.exe"}',
                    str(PROJECT / 'packaging/update_safety.cs'), str(PROJECT / 'packaging/updater.cs')], check=True)

    def bundle(version):
        folder = root / ('bundle-' + version)
        (folder / 'app').mkdir(parents=True)
        (folder / 'runtime').mkdir()
        (folder / 'app/release.json').write_text(json.dumps({'version':version}))
        (folder / 'app/main.py').write_text('source for ' + version)
        (folder / 'runtime/python.exe').write_bytes(b'unchanged synthetic runtime')
        (folder / 'NeckerExperiment.exe').write_bytes(b'not executable; never launched')
        if version == '1.2': (folder / 'app/new.py').write_text('new module')
        manifest = {p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
        (folder / 'manifest.json').write_text(json.dumps(manifest))
        return folder

    source, target = bundle('1.1'), bundle('1.2')
    dist = root / 'dist'; dist.mkdir()
    for version, folder, patch_mode in [('1.1',source,False), ('1.2',target,False), ('1.2',target,True)]:
        build = root / (('patch-' if patch_mode else 'full-') + version)
        prepare(folder, build, source / 'manifest.json' if patch_mode else None,
                digest(source / 'manifest.json') if patch_mode else None, '1.1' if patch_mode else None)
        args = [str(ISCC), '/Qp', f'/DAppVersion={version}', f'/DAppIdGuid={guid}', f'/DBundleRoot={folder}',
                f'/DInstallerOutput={dist}', f'/DPayloadList={build / "payload.iss"}', f'/DVerifierExe={verifier}']
        if patch_mode: args += ['/DPatchFromVersion=1.1', f'/DSourceManifest={source / "manifest.json"}']
        with (root / f'compile-{build.name}.log').open('w') as log:
            subprocess.run(args + [str(PROJECT / 'packaging/necker.iss')], stdout=log, stderr=subprocess.STDOUT, check=True)
    prefix = 'Nicholas-Nice-Necker-Cube-Experiment'
    def install(name, expected=0):
        exe = dist / f'{prefix}-{name}-x64.exe'
        result = subprocess.run([str(exe), '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',
            '/NOICONS','/NOSHORTCUTS=1','/NOLAUNCH=1', f'/DIR={installed}', f'/LOG={root / (name + "-" + str(time.time_ns()) + ".log")}'], timeout=60)
        if expected == 0: assert result.returncode == 0, (name,result.returncode)
        else: assert result.returncode != 0, (name,'unexpected success')
    def registered():
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
            assert Path(winreg.QueryValueEx(key,'InstallLocation')[0]).resolve() == installed.resolve()
            return winreg.QueryValueEx(key,'DisplayVersion')[0]
    install('Setup-1.1')
    assert registered() == '1.1'
    user_file = installed / 'user-note.txt'; user_file.write_text('preserve')
    linked = root / 'linked-runtime.bin'
    linked.hardlink_to(installed / 'runtime/python.exe')
    install('Patch-1.1-to-1.2', expected=1)
    linked.unlink()
    (installed / 'runtime/python.exe').write_text('unexpected modification')
    old = (installed / 'app/main.py').read_bytes()
    install('Patch-1.1-to-1.2', expected=1)
    assert (installed / 'app/main.py').read_bytes() == old
    assert registered() == '1.1'
    install('Setup-1.1')  # Repair the intentionally corrupt fixture runtime.
    stamp = (installed / 'runtime/python.exe').stat().st_mtime_ns
    # Durable known-state retry: simulate interruption after one new file is copied.
    result = subprocess.run([str(verifier),'prepare',str(installed),str(source/'manifest.json'),
                            str(target/'manifest.json'),'1.1','1.2','{' + guid + '}'])
    assert result.returncode == 0
    shutil.copy2(target / 'app/main.py', installed / 'app/main.py')
    install('Patch-1.1-to-1.2')
    assert registered() == '1.2'
    assert (installed / 'runtime/python.exe').stat().st_mtime_ns == stamp
    assert not (installed / 'necker-patch-pending.txt').exists()
    assert (installed / 'app/new.py').is_file()
    install('Patch-1.1-to-1.2', expected=1)  # Wrong baseline, no implicit downgrade/retry.
    # An arbitrary timestamp distinguishes a skipped file from a rewrite that
    # merely restores the original packaged timestamp.
    stamp += 13000000000
    os.utime(installed / 'runtime/python.exe', ns=(stamp, stamp))
    install('Setup-1.2')
    assert (installed / 'runtime/python.exe').stat().st_mtime_ns == stamp
    # A failed target verification returns the required repair exit code.
    (installed / 'app/main.py').write_text('corrupt target')
    check = subprocess.run([str(verifier),'finish',str(installed),str(source/'manifest.json'),
                            str(target/'manifest.json'),'1.1','1.2','{' + guid + '}'], capture_output=True)
    assert check.returncode == 12
    install('Setup-1.2')
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
        uninstaller = Path(winreg.QueryValueEx(key,'UninstallString')[0].strip('"'))
    assert uninstaller.resolve().parent == installed.resolve()
    subprocess.run([str(uninstaller),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],check=True,timeout=60)
    assert user_file.read_text() == 'preserve'
    report = {'passed':True,'registration':guid,'fresh_install':True,'tampered_baseline_blocked':True,
              'partial_patch_recovered':True,'wrong_source_blocked':True,'runtime_not_rewritten':True,
              'full_repair':True,'hardlinks_rejected':True,'target_mismatch_exit_12':True,'uninstall_preserved_unknown_files':True}
    (root / 'report.json').write_text(json.dumps(report,indent=2))
    print(root / 'report.json', flush=True)


if __name__ == '__main__': main()
