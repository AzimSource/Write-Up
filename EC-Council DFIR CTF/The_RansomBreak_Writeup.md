# Level 4 – Ransomware Analysis and Decryption

## The RansomBreak

## Scenario

A Windows victim reported that files inside the following directory had been encrypted by ransomware:

```text
C:\Users\Admin\Documents\CTF_Vault
```

The objective was to analyze the supplied `Rasome` executable, identify its installation path, framework version, packer, and key-generation function, calculate the victim-specific decryption key, and finally recover the flag from `Flag.txt`.

> Perform malware analysis only inside the isolated lab VM. Do not execute the sample on a personal or production system.

## Tools Used

- Detect It Easy (DIE)
- dnSpy or another .NET decompiler
- PowerShell
- Rasome's built-in decryption interface
- Notepad

## Final Answers

| Challenge | Answer |
|---|---|
| 1 – Full executable path | `C:\Users\Admin\AppData\Local\Rasome\Rasome.exe` |
| 2 – .NET Framework version | `v4.0.30319` |
| 3 – Packer | `MPRESS` |
| 4 – Key-generation function | `GenerateKeyFromMachineNameMD5` |
| 5 – Calculated decryption key | `037E39A5C57380EA9357167684CA4DD7` |
| 6 – Decrypted flag | `flag{b4CKup_Sav3D_7h3_$YsTeM}` |

---

## Challenge 1 – Identify the Rasome Executable Path

The malware's strings and decompiled code reveal the location used for the Rasome executable:

```text
C:\Users\Admin\AppData\Local\Rasome\Rasome.exe
```

**Answer:**

```text
C:\Users\Admin\AppData\Local\Rasome\Rasome.exe
```

## Challenge 2 – Identify the .NET Framework Version

1. Open the packed Rasome executable in **Detect It Easy**.
2. Examine the executable's PE and CLR/.NET information.
3. The linked CLR version is displayed as `v4.0.30319`.

**Answer:**

```text
v4.0.30319
```

## Challenge 3 – Identify the Packer

1. Continue examining the executable in **Detect It Easy**.
2. Review the packer/signature detection result.
3. The executable is identified as being packed with **MPRESS**.

**Answer:**

```text
MPRESS
```

## Challenge 4 – Identify the Key-Generation Function

1. Open the .NET assembly in **dnSpy**.
2. Search the decompiled classes for code related to encryption, decryption, `MD5`, or `MachineName`.
3. Inspect the method used to derive the ransomware key.
4. The relevant function is named:

```text
GenerateKeyFromMachineNameMD5
```

The name describes its behavior: it obtains the Windows computer name, converts it to bytes, calculates its MD5 digest, and represents the 16-byte digest as a 32-character hexadecimal string.

**Answer:**

```text
GenerateKeyFromMachineNameMD5
```

## Challenge 5 – Calculate the Machine-Specific Decryption Key

The decompiled function showed that the key is the uppercase MD5 hash of the victim's Windows machine name.

### Obtain the key with PowerShell

Open a normal PowerShell window inside the Windows Victim VM and paste the following command directly at its prompt:

```powershell
$n=[Environment]::MachineName; $m=[Security.Cryptography.MD5]::Create(); $k=-join ($m.ComputeHash([Text.Encoding]::UTF8.GetBytes($n)) | ForEach-Object {$_.ToString('X2')}); Write-Host "Machine name: $n"; Write-Host "Decryption key: $k"
```

The calculated value is:

```text
037E39A5C57380EA9357167684CA4DD7
```

### Why the earlier command produced a parser error

Running `powershell -Command "..."` from an existing PowerShell prompt caused the outer shell to expand variables such as `$n`, `$m`, and `$k` before the command reached the new process. The variables consequently disappeared from the inner command, producing errors such as `An expression was expected after '('`. Running the code directly in the current PowerShell session avoids the nested quoting and expansion problem.

**Answer:**

```text
037E39A5C57380EA9357167684CA4DD7
```

## Challenge 6 – Decrypt Flag.txt

1. Return to the already-running Rasome interface in the isolated lab VM.
2. Enter the calculated key:

   ```text
   037E39A5C57380EA9357167684CA4DD7
   ```

3. Click the application's **Decrypt** button.
4. Browse to:

   ```text
   C:\Users\Admin\Documents\CTF_Vault
   ```

5. Open `Flag.txt` in Notepad.
6. The recovered content is:

   ```text
   flag{b4CKup_Sav3D_7h3_$YsTeM}
   ```

**Answer:**

```text
flag{b4CKup_Sav3D_7h3_$YsTeM}
```

## Conclusion

Static analysis identified the sample as a packed .NET executable and revealed that it derives its encryption/decryption key from the victim computer's name using MD5. Reproducing this operation in PowerShell produced the correct 32-character key. Supplying that key to the ransomware's decryption function restored `Flag.txt` and exposed the final flag.
