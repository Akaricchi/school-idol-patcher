# School Idol Patcher
A tool that creates "rootpatched" versions of [Love Live! School Idol Festival](https://www.school-fes.klabgames.net/) APKs. It disables the game's `su` binary detection, allowing it to work on "rooted" devices. It also adds the "write to external storage" permission, making it possible to move the game's data outside of the system partition (e.g. to the SD card) on space-constrainted systems. Works with the Japanese versions as well as the worldwide ones (and possibly others).

# Requirements

* Python 3 (3.5 or above recommended)
* Apktool (2.2.1 recommended)
* jarsigner (recommended but optional, you can use another compatible tool to sign the APK)

# Usage

First of all, you have to obtain the original APK from KLab. Various methods exist, but they are outside the scope of this guide.

Android requires all apps to be [digitally signed](https://source.android.com/security/apksigning/) in order to be installable. This tool can (mostly) handle this for you, or you can opt to manually sign the patched APK if you know what you're doing.

#### Option 1: patch and sign in one command (recommended)

This method requires `jarsigner` to be installed.

If you have never signed an APK before, you will have to [create a Java keystore](https://www.digitalocean.com/community/tutorials/java-keytool-essentials-working-with-java-keystores) first. When you have a keystore, proceed:

```
python3 sif-original.apk -o sif-patched.apk -s your_key_alias -k your_keystore.jks
```

If everything goes well, you will be asked for your keystore password after some time.

#### Option 2: patch, then manually sign the APK

You can instruct the script to only patch the APK and not care about signing at all:

```
python3 sif-original.apk -o sif-patched.apk
```

You will then have to sign `sif-patched.apk` yourself. 

# Known issues

* If you try to install the rootpatched APK over the original SIF app or someone else's rootpatch (aka "upgrade" it), it will fail because the signatures differ. This is a security measure of Android and there's no getting around it. You will have to uninstall the app first in this case, then install your rootpatched version. Upgrades with matching signatures should work just fine.
* **Google account linking and in-app purchases will not work**. This is for similar reasons and I can't do anything about that either. As you're on a rooted device, however, you can keep a backup of the `/data/data/klb.android.lovelive/shared_prefs/GameEngineActivity.xml` file, which contains authentication information for your SIF account. This is **not** a substitute for keeping your transfer ID and password around, though! Also, transfering the account to another device will invalidate that file.

# Disclaimer

Producing and/or using modified versions of School Idol Festival in any way is against KLab's terms of service. Use this tool at your own risk. I am not responsible for any potential damage to your account(s) and/or device(s).
