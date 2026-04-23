<img width="504" height="407" alt="image" src="https://github.com/user-attachments/assets/c9ed00d0-b1d7-4393-aa22-209b218f6799" />

## Phase 1: Initial Reconnaissance & Decompilation

Our first step is to unpack the provided Android application to understand its structure and look for obvious clues.

**1. Decompile the APK using Apktool:**

`apktool d chall.apk -o chall_decompiled
cd chall_decompiled`

<img width="719" height="481" alt="image" src="https://github.com/user-attachments/assets/0f71c143-85af-4027-baa5-b91e06da386e" />

**2. Inspect the Android Manifest:**

`cat AndroidManifest.xml`

<img width="1432" height="287" alt="image" src="https://github.com/user-attachments/assets/9f3fb565-69d5-4b28-af00-7dfd4b94cac4" />

**3. Inspect the Assets Folder:**

`ls -la assets/`

<img width="489" height="128" alt="image" src="https://github.com/user-attachments/assets/b7c09ad5-9f5b-4f26-b9a2-92b90899c8a4" />

## Phase 2: Extracting the Decoy Image

Investigating the `background.txt` file reveals it is not text, but a Base64-encoded image wrapped in CSS syntax.

**4. Decode the Base64 Decoy Image:**

`sed 's/url(data:image\/jpeg;base64,//' assets/background.txt | sed 's/)//' | base64 -d > ../hidden_flag.jpg`

<img width="987" height="55" alt="image" src="https://github.com/user-attachments/assets/05c0c792-94ac-4648-affb-2619b39d8294" />

## Phase 3: Defeating the First-Stage Packer

Since the APK is packed, the real application bytecode is hidden. We must analyze the `ProxyApplication` Smali code to see how it unpacks the real app at runtime.

**5. Find the Decryption Routine in the Packer:**

```jsx
sed -n '/\.method private decrypt/,/\.end method/p' smali/com/example/reforceapk/ProxyApplication.smali
```

<img width="900" height="567" alt="image" src="https://github.com/user-attachments/assets/e2d1aa3c-c417-4cb1-8d4e-a2b26f8474e4" />

**6. Extract and Decrypt the Original `classes.dex`:**

`cd ..
unzip chall.apk classes.dex`

<img width="463" height="81" alt="image" src="https://github.com/user-attachments/assets/bb575fbc-f977-44bf-b37f-5a8e11ba126f" />

Create and run the decryption script (`decrypt.py`):

Python

`with open('classes.dex', 'rb') as f:
    data = f.read()
# XOR every byte with 0xFF to decrypt the payload
decrypted = bytes([b ^ 0xFF for b in data])
with open('decrypted.bin', 'wb') as f:
    f.write(decrypted)
print("Decryption complete! Saved as decrypted.bin")`

<img width="471" height="238" alt="image" src="https://github.com/user-attachments/assets/2feb8599-45cb-46b8-bfd9-50a997aa9d1d" />

`python3 decrypt.py`

**7. Carve the Real APK out of the Decrypted Binary:**
Using `binwalk`, we determine the real APK starts at byte `14332`. We extract it using `dd`.

`dd if=decrypted.bin of=real_app.apk bs=1 skip=14332`

<img width="1205" height="362" alt="image" src="https://github.com/user-attachments/assets/9c9e53a5-53d3-4cb8-a379-2e976c0512d8" />

<img width="773" height="98" alt="image" src="https://github.com/user-attachments/assets/c2900b9d-ca5d-427a-8772-6e29dae226a6" />

## Phase 4: Bypassing Anti-Analysis & Java Reversing

The extracted `real_app.apk` has intentionally corrupted ZIP headers (a "zip bomb" technique) to break standard analysis tools like `unzip` and `apktool`.

**8. Force Extraction using 7-Zip:**

`7z x real_app.apk -oforced_extraction`

<img width="773" height="98" alt="image" src="https://github.com/user-attachments/assets/145bf346-f7d0-4236-83ae-98e454a913f7" />

**9. Decompile the Real Application Logic:**
We bypass `jadx` pathing bugs by providing absolute paths.

`mkdir -p real_source
jadx -d "$(pwd)/real_source" "$(pwd)/forced_extraction/classes.dex"
cd real_source`

<img width="721" height="545" alt="image" src="https://github.com/user-attachments/assets/a80f0f7c-daf3-4dae-a870-0f13073b0e49" />

**10. Discover Native C++ Calls:**
Searching the Java source code reveals that the encryption logic is handed off to a native C++ library.

`grep -ri "native" .`

<img width="1038" height="145" alt="image" src="https://github.com/user-attachments/assets/58e567e9-f25a-4ca2-b6ee-dc2199f99865" />

## Phase 5: Analyzing the Native Library

The Java code takes the decoy image, encrypts it using `libnative-lib.so`, and saves it as `background.bkp`. We must analyze the C++ assembly to find the encryption key.

**11. Disassemble the Native Library:**

```jsx
objdump -d -M intel ../forced_extraction/lib/x86_64/libnative-lib.so | grep -A 30 "generateKeyBuf"
```

<img width="1011" height="662" alt="image" src="https://github.com/user-attachments/assets/56704475-478c-46dd-b955-e60fd75864f6" />

```jsx
0000000000066360 <_Z14generateKeyBufv@@Base-0x60>:
   66360:       48 8d 3d d9 6c 07 00    lea    rdi,[rip+0x76cd9]        # dd040 <pthread_rwlock_rdlock@plt+0x4010>
   66367:       e9 64 14 07 00          jmp    d77d0 <__cxa_finalize@plt>
   6636c:       0f 1f 40 00             nop    DWORD PTR [rax+0x0]
   66370:       c3                      ret
   66371:       66 66 66 66 66 66 2e    data16 data16 data16 data16 data16 cs nop WORD PTR [rax+rax*1+0x0]
   66378:       0f 1f 84 00 00 00 00 
   6637f:       00 
   66380:       e9 ab d1 06 00          jmp    d3530 <__emutls_get_address@@Base+0x1d0>
   66385:       66 66 2e 0f 1f 84 00    data16 cs nop WORD PTR [rax+rax*1+0x0]
   6638c:       00 00 00 00 
   66390:       48 85 ff                test   rdi,rdi
   66393:       74 02                   je     66397 <_ZTSN10__cxxabiv121__vmi_class_type_infoE@@Base+0x19528>
   66395:       ff e7                   jmp    rdi
   66397:       c3                      ret
   66398:       0f 1f 84 00 00 00 00    nop    DWORD PTR [rax+rax*1+0x0]
   6639f:       00 
   663a0:       48 89 fe                mov    rsi,rdi
   663a3:       48 8d 3d e6 ff ff ff    lea    rdi,[rip+0xffffffffffffffe6]        # 66390 <_ZTSN10__cxxabiv121__vmi_class_type_infoE@@Base+0x19521>
   663aa:       48 8d 15 8f 6c 07 00    lea    rdx,[rip+0x76c8f]        # dd040 <pthread_rwlock_rdlock@plt+0x4010>
   663b1:       e9 2a 14 07 00          jmp    d77e0 <__cxa_atexit@plt>
   663b6:       cc                      int3
   663b7:       cc                      int3
   663b8:       cc                      int3
   663b9:       cc                      int3
   663ba:       cc                      int3
   663bb:       cc                      int3
   663bc:       cc                      int3
   663bd:       cc                      int3
   663be:       cc                      int3
   663bf:       cc                      int3

00000000000663c0 <_Z14generateKeyBufv@@Base>:
   663c0:       55                      push   rbp
   663c1:       48 89 e5                mov    rbp,rsp
   663c4:       48 81 ec c0 01 00 00    sub    rsp,0x1c0
   663cb:       48 89 bd 90 fe ff ff    mov    QWORD PTR [rbp-0x170],rdi
   663d2:       48 89 f8                mov    rax,rdi
   663d5:       48 89 85 98 fe ff ff    mov    QWORD PTR [rbp-0x168],rax
   663dc:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   663e3:       00 00 
   663e5:       48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
   663e9:       48 89 bd 18 ff ff ff    mov    QWORD PTR [rbp-0xe8],rdi
   663f0:       80 3d 81 34 08 00 00    cmp    BYTE PTR [rip+0x83481],0x0        # e9878 <__cxa_unexpected_handler@@Base+0x70>
   663f7:       75 43                   jne    6643c <_Z14generateKeyBufv@@Base+0x7c>
   663f9:       48 8d 3d 78 34 08 00    lea    rdi,[rip+0x83478]        # e9878 <__cxa_unexpected_handler@@Base+0x70>
   66400:       e8 fb 13 07 00          call   d7800 <__cxa_guard_acquire@plt>
   66405:       83 f8 00                cmp    eax,0x0
   66408:       74 32                   je     6643c <_Z14generateKeyBufv@@Base+0x7c>
   6640a:       48 8d 3d 4f 34 08 00    lea    rdi,[rip+0x8344f]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66411:       e8 ca 05 00 00          call   669e0 <_Z14generateKeyBufv@@Base+0x620>
   66416:       48 8d 3d 03 06 00 00    lea    rdi,[rip+0x603]        # 66a20 <_Z14generateKeyBufv@@Base+0x660>
   6641d:       48 8d 35 3c 34 08 00    lea    rsi,[rip+0x8343c]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66424:       48 8d 15 15 6c 07 00    lea    rdx,[rip+0x76c15]        # dd040 <pthread_rwlock_rdlock@plt+0x4010>
   6642b:       e8 b0 13 07 00          call   d77e0 <__cxa_atexit@plt>
   66430:       48 8d 3d 41 34 08 00    lea    rdi,[rip+0x83441]        # e9878 <__cxa_unexpected_handler@@Base+0x70>
   66437:       e8 d4 13 07 00          call   d7810 <__cxa_guard_release@plt>
   6643c:       f6 05 3d 34 08 00 01    test   BYTE PTR [rip+0x8343d],0x1        # e9880 <__cxa_unexpected_handler@@Base+0x78>
   66443:       0f 85 c6 02 00 00       jne    6670f <_Z14generateKeyBufv@@Base+0x34f>
   66449:       8b 05 b1 1b fe ff       mov    eax,DWORD PTR [rip+0xfffffffffffe1bb1]        # 48000 <__llvm_fs_discriminator__@@Base-0x1d63>
   6644f:       89 45 bc                mov    DWORD PTR [rbp-0x44],eax
   66452:       8b 05 8c 1b fe ff       mov    eax,DWORD PTR [rip+0xfffffffffffe1b8c]        # 47fe4 <__llvm_fs_discriminator__@@Base-0x1d7f>
   66458:       89 45 b8                mov    DWORD PTR [rbp-0x48],eax
   6645b:       8b 05 8b 1b fe ff       mov    eax,DWORD PTR [rip+0xfffffffffffe1b8b]        # 47fec <__llvm_fs_discriminator__@@Base-0x1d77>
   66461:       89 45 b4                mov    DWORD PTR [rbp-0x4c],eax
   66464:       8b 05 a2 1b fe ff       mov    eax,DWORD PTR [rip+0xfffffffffffe1ba2]        # 4800c <__llvm_fs_discriminator__@@Base-0x1d57>
   6646a:       89 45 b0                mov    DWORD PTR [rbp-0x50],eax
   6646d:       8b 05 7d 1b fe ff       mov    eax,DWORD PTR [rip+0xfffffffffffe1b7d]        # 47ff0 <__llvm_fs_discriminator__@@Base-0x1d73>
   66473:       89 45 ac                mov    DWORD PTR [rbp-0x54],eax
   66476:       48 8d 3d e3 33 08 00    lea    rdi,[rip+0x833e3]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   6647d:       e8 8e 06 00 00          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   66482:       48 89 45 98             mov    QWORD PTR [rbp-0x68],rax
   66486:       48 8d 7d a0             lea    rdi,[rbp-0x60]
   6648a:       48 8d 75 98             lea    rsi,[rbp-0x68]
   6648e:       e8 8d 13 07 00          call   d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>
   66493:       48 8d 55 bc             lea    rdx,[rbp-0x44]
   66497:       48 8d 4d bc             lea    rcx,[rbp-0x44]
   6649b:       48 83 c1 04             add    rcx,0x4
   6649f:       48 8b 75 a0             mov    rsi,QWORD PTR [rbp-0x60]
   664a3:       48 8d 3d b6 33 08 00    lea    rdi,[rip+0x833b6]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   664aa:       e8 81 13 07 00          call   d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>
   664af:       48 89 85 10 ff ff ff    mov    QWORD PTR [rbp-0xf0],rax
   664b6:       48 8d 3d a3 33 08 00    lea    rdi,[rip+0x833a3]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   664bd:       e8 4e 06 00 00          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   664c2:       48 89 45 88             mov    QWORD PTR [rbp-0x78],rax
   664c6:       48 8d 7d 90             lea    rdi,[rbp-0x70]
   664ca:       48 8d 75 88             lea    rsi,[rbp-0x78]
   664ce:       e8 4d 13 07 00          call   d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>
   664d3:       48 8d 55 b8             lea    rdx,[rbp-0x48]
   664d7:       48 8d 4d b8             lea    rcx,[rbp-0x48]
   664db:       48 83 c1 04             add    rcx,0x4
   664df:       48 8b 75 90             mov    rsi,QWORD PTR [rbp-0x70]
   664e3:       48 8d 3d 76 33 08 00    lea    rdi,[rip+0x83376]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   664ea:       e8 41 13 07 00          call   d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>
   664ef:       48 89 85 08 ff ff ff    mov    QWORD PTR [rbp-0xf8],rax
   664f6:       48 8d 3d 63 33 08 00    lea    rdi,[rip+0x83363]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   664fd:       e8 0e 06 00 00          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   66502:       48 89 85 78 ff ff ff    mov    QWORD PTR [rbp-0x88],rax
   66509:       48 8d 7d 80             lea    rdi,[rbp-0x80]
   6650d:       48 8d b5 78 ff ff ff    lea    rsi,[rbp-0x88]
   66514:       e8 07 13 07 00          call   d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>
   66519:       48 8d 55 b4             lea    rdx,[rbp-0x4c]
   6651d:       48 8d 4d b4             lea    rcx,[rbp-0x4c]
   66521:       48 83 c1 04             add    rcx,0x4
   66525:       48 8b 75 80             mov    rsi,QWORD PTR [rbp-0x80]
   66529:       48 8d 3d 30 33 08 00    lea    rdi,[rip+0x83330]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66530:       e8 fb 12 07 00          call   d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>
   66535:       48 89 85 00 ff ff ff    mov    QWORD PTR [rbp-0x100],rax
   6653c:       48 8d 3d 1d 33 08 00    lea    rdi,[rip+0x8331d]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66543:       e8 c8 05 00 00          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   66548:       48 89 85 68 ff ff ff    mov    QWORD PTR [rbp-0x98],rax
   6654f:       48 8d bd 70 ff ff ff    lea    rdi,[rbp-0x90]
   66556:       48 8d b5 68 ff ff ff    lea    rsi,[rbp-0x98]
   6655d:       e8 be 12 07 00          call   d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>
   66562:       48 8d 55 b0             lea    rdx,[rbp-0x50]
   66566:       48 8d 4d b0             lea    rcx,[rbp-0x50]
   6656a:       48 83 c1 04             add    rcx,0x4
   6656e:       48 8b b5 70 ff ff ff    mov    rsi,QWORD PTR [rbp-0x90]
   66575:       48 8d 3d e4 32 08 00    lea    rdi,[rip+0x832e4]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   6657c:       e8 af 12 07 00          call   d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>
   66581:       48 89 85 f8 fe ff ff    mov    QWORD PTR [rbp-0x108],rax
   66588:       48 8d 3d d1 32 08 00    lea    rdi,[rip+0x832d1]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   6658f:       e8 7c 05 00 00          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   66594:       48 89 85 58 ff ff ff    mov    QWORD PTR [rbp-0xa8],rax
   6659b:       48 8d bd 60 ff ff ff    lea    rdi,[rbp-0xa0]
   665a2:       48 8d b5 58 ff ff ff    lea    rsi,[rbp-0xa8]
   665a9:       e8 72 12 07 00          call   d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>
   665ae:       48 8d 55 ac             lea    rdx,[rbp-0x54]
   665b2:       48 8d 4d ac             lea    rcx,[rbp-0x54]
   665b6:       48 83 c1 04             add    rcx,0x4
   665ba:       48 8b b5 60 ff ff ff    mov    rsi,QWORD PTR [rbp-0xa0]
   665c1:       48 8d 3d 98 32 08 00    lea    rdi,[rip+0x83298]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   665c8:       e8 63 12 07 00          call   d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>
   665cd:       48 89 85 f0 fe ff ff    mov    QWORD PTR [rbp-0x110],rax
   665d4:       48 c7 85 e8 fe ff ff    mov    QWORD PTR [rbp-0x118],0x0
   665db:       00 00 00 00 
   665df:       48 8b 85 e8 fe ff ff    mov    rax,QWORD PTR [rbp-0x118]
   665e6:       48 89 85 88 fe ff ff    mov    QWORD PTR [rbp-0x178],rax
   665ed:       48 8d 3d 6c 32 08 00    lea    rdi,[rip+0x8326c]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
--
   6660a:       0f 83 f8 00 00 00       jae    66708 <_Z14generateKeyBufv@@Base+0x348>
   66610:       48 c7 85 e0 fe ff ff    mov    QWORD PTR [rbp-0x120],0x0
   66617:       00 00 00 00 
   6661b:       48 8b 85 e0 fe ff ff    mov    rax,QWORD PTR [rbp-0x120]
   66622:       48 89 85 80 fe ff ff    mov    QWORD PTR [rbp-0x180],rax
   66629:       48 8d 3d 30 32 08 00    lea    rdi,[rip+0x83230]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66630:       e8 3b 05 00 00          call   66b70 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x20>
   66635:       48 89 c1                mov    rcx,rax
   66638:       48 8b 85 80 fe ff ff    mov    rax,QWORD PTR [rbp-0x180]
   6663f:       48 2b 8d e8 fe ff ff    sub    rcx,QWORD PTR [rbp-0x118]
   66646:       48 83 e9 01             sub    rcx,0x1
   6664a:       48 39 c8                cmp    rax,rcx
   6664d:       0f 83 9c 00 00 00       jae    666ef <_Z14generateKeyBufv@@Base+0x32f>
   66653:       48 8b b5 e0 fe ff ff    mov    rsi,QWORD PTR [rbp-0x120]
   6665a:       48 8d 3d ff 31 08 00    lea    rdi,[rip+0x831ff]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66661:       e8 2a 05 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   66666:       0f b6 00                movzx  eax,BYTE PTR [rax]
   66669:       89 85 7c fe ff ff       mov    DWORD PTR [rbp-0x184],eax
   6666f:       48 8b b5 e0 fe ff ff    mov    rsi,QWORD PTR [rbp-0x120]
   66676:       48 83 c6 01             add    rsi,0x1
   6667a:       48 8d 3d df 31 08 00    lea    rdi,[rip+0x831df]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66681:       e8 0a 05 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   66686:       48 89 c1                mov    rcx,rax
   66689:       8b 85 7c fe ff ff       mov    eax,DWORD PTR [rbp-0x184]
   6668f:       0f b6 09                movzx  ecx,BYTE PTR [rcx]
   66692:       39 c8                   cmp    eax,ecx
   66694:       7e 40                   jle    666d6 <_Z14generateKeyBufv@@Base+0x316>
   66696:       48 8b b5 e0 fe ff ff    mov    rsi,QWORD PTR [rbp-0x120]
   6669d:       48 8d 3d bc 31 08 00    lea    rdi,[rip+0x831bc]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   666a4:       e8 e7 04 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   666a9:       48 89 85 70 fe ff ff    mov    QWORD PTR [rbp-0x190],rax
   666b0:       48 8b b5 e0 fe ff ff    mov    rsi,QWORD PTR [rbp-0x120]
   666b7:       48 83 c6 01             add    rsi,0x1
   666bb:       48 8d 3d 9e 31 08 00    lea    rdi,[rip+0x8319e]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   666c2:       e8 c9 04 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   666c7:       48 8b bd 70 fe ff ff    mov    rdi,QWORD PTR [rbp-0x190]
   666ce:       48 89 c6                mov    rsi,rax
   666d1:       e8 da 04 00 00          call   66bb0 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x60>
   666d6:       eb 00                   jmp    666d8 <_Z14generateKeyBufv@@Base+0x318>
   666d8:       48 8b 85 e0 fe ff ff    mov    rax,QWORD PTR [rbp-0x120]
   666df:       48 83 c0 01             add    rax,0x1
   666e3:       48 89 85 e0 fe ff ff    mov    QWORD PTR [rbp-0x120],rax
   666ea:       e9 2c ff ff ff          jmp    6661b <_Z14generateKeyBufv@@Base+0x25b>
   666ef:       eb 00                   jmp    666f1 <_Z14generateKeyBufv@@Base+0x331>
   666f1:       48 8b 85 e8 fe ff ff    mov    rax,QWORD PTR [rbp-0x118]
   666f8:       48 83 c0 01             add    rax,0x1
   666fc:       48 89 85 e8 fe ff ff    mov    QWORD PTR [rbp-0x118],rax
   66703:       e9 d7 fe ff ff          jmp    665df <_Z14generateKeyBufv@@Base+0x21f>
   66708:       c6 05 71 31 08 00 01    mov    BYTE PTR [rip+0x83171],0x1        # e9880 <__cxa_unexpected_handler@@Base+0x78>
   6670f:       48 8d 3d 4a 31 08 00    lea    rdi,[rip+0x8314a]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66716:       e8 c5 04 00 00          call   66be0 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x90>
   6671b:       48 89 85 50 ff ff ff    mov    QWORD PTR [rbp-0xb0],rax
   66722:       48 8d 7d c0             lea    rdi,[rbp-0x40]
   66726:       48 89 bd 68 fe ff ff    mov    QWORD PTR [rbp-0x198],rdi
   6672d:       e8 0e 11 07 00          call   d7840 <_ZN4SHA1C2Ev@plt>
   66732:       48 8b bd 68 fe ff ff    mov    rdi,QWORD PTR [rbp-0x198]
   66739:       48 8d b5 50 ff ff ff    lea    rsi,[rbp-0xb0]
   66740:       ba 08 00 00 00          mov    edx,0x8
   66745:       e8 06 11 07 00          call   d7850 <_ZN4SHA16updateEPKvm@plt>
   6674a:       eb 00                   jmp    6674c <_Z14generateKeyBufv@@Base+0x38c>
   6674c:       48 8d bd 38 ff ff ff    lea    rdi,[rbp-0xc8]
   66753:       48 8d 75 c0             lea    rsi,[rbp-0x40]
   66757:       e8 04 11 07 00          call   d7860 <_ZN4SHA15finalEv@plt>
   6675c:       eb 00                   jmp    6675e <_Z14generateKeyBufv@@Base+0x39e>
   6675e:       48 8d bd 38 ff ff ff    lea    rdi,[rbp-0xc8]
   66765:       48 89 bd 60 fe ff ff    mov    QWORD PTR [rbp-0x1a0],rdi
   6676c:       e8 ff 06 00 00          call   66e70 <_ZN4SHA15finalEv@@Base+0x180>
   66771:       48 8b bd 60 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1a0]
   66778:       48 89 85 c8 fe ff ff    mov    QWORD PTR [rbp-0x138],rax
   6677f:       e8 3c 07 00 00          call   66ec0 <_ZN4SHA15finalEv@@Base+0x1d0>
   66784:       48 89 85 c0 fe ff ff    mov    QWORD PTR [rbp-0x140],rax
   6678b:       48 8b b5 c8 fe ff ff    mov    rsi,QWORD PTR [rbp-0x138]
   66792:       48 8b 95 c0 fe ff ff    mov    rdx,QWORD PTR [rbp-0x140]
   66799:       48 8d bd 20 ff ff ff    lea    rdi,[rbp-0xe0]
   667a0:       e8 cb 10 07 00          call   d7870 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEEC2B8ne210000INS_11__wrap_iterIPcEETnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS9_E9referenceEEE5valueEiE4typeELi0EEES9_S9_@plt>
   667a5:       eb 00                   jmp    667a7 <_Z14generateKeyBufv@@Base+0x3e7>
   667a7:       48 8d 3d b2 30 08 00    lea    rdi,[rip+0x830b2]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   667ae:       e8 bd 03 00 00          call   66b70 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x20>
   667b3:       48 8b bd 90 fe ff ff    mov    rdi,QWORD PTR [rbp-0x170]
   667ba:       48 83 c0 08             add    rax,0x8
   667be:       48 89 85 b8 fe ff ff    mov    QWORD PTR [rbp-0x148],rax
   667c5:       c6 85 b7 fe ff ff 00    mov    BYTE PTR [rbp-0x149],0x0
   667cc:       be 20 00 00 00          mov    esi,0x20
   667d1:       e8 ea 07 00 00          call   66fc0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEEC2B8ne210000INS_11__wrap_iterIPcEETnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS9_E9referenceEEE5valueEiE4typeELi0EEES9_S9_@@Base+0xb0>
   667d6:       eb 00                   jmp    667d8 <_Z14generateKeyBufv@@Base+0x418>
   667d8:       48 c7 85 a8 fe ff ff    mov    QWORD PTR [rbp-0x158],0x0
   667df:       00 00 00 00 
   667e3:       48 83 bd a8 fe ff ff    cmp    QWORD PTR [rbp-0x158],0x20
   667ea:       20 
   667eb:       0f 83 47 01 00 00       jae    66938 <_Z14generateKeyBufv@@Base+0x578>
   667f1:       48 b8 2d 7f 95 4c 2d    movabs rax,0x5851f42d4c957f2d
   667f8:       f4 51 58 
   667fb:       48 0f af 85 b8 fe ff    imul   rax,QWORD PTR [rbp-0x148]
   66802:       ff 
   66803:       48 83 c0 01             add    rax,0x1
   66807:       48 89 85 b8 fe ff ff    mov    QWORD PTR [rbp-0x148],rax
   6680e:       48 8b 85 b8 fe ff ff    mov    rax,QWORD PTR [rbp-0x148]
   66815:       48 c1 e8 21             shr    rax,0x21
   66819:       89 85 a4 fe ff ff       mov    DWORD PTR [rbp-0x15c],eax
   6681f:       48 8b 85 a8 fe ff ff    mov    rax,QWORD PTR [rbp-0x158]
   66826:       48 89 85 48 fe ff ff    mov    QWORD PTR [rbp-0x1b8],rax
   6682d:       48 8d bd 20 ff ff ff    lea    rdi,[rbp-0xe0]
   66834:       e8 37 03 00 00          call   66b70 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x20>
   66839:       48 89 c1                mov    rcx,rax
   6683c:       48 8b 85 48 fe ff ff    mov    rax,QWORD PTR [rbp-0x1b8]
   66843:       31 d2                   xor    edx,edx
   66845:       48 f7 f1                div    rcx
   66848:       48 89 d6                mov    rsi,rdx
   6684b:       48 8d bd 20 ff ff ff    lea    rdi,[rbp-0xe0]
   66852:       e8 39 03 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   66857:       8a 00                   mov    al,BYTE PTR [rax]
   66859:       88 85 a3 fe ff ff       mov    BYTE PTR [rbp-0x15d],al
   6685f:       48 8b 85 a8 fe ff ff    mov    rax,QWORD PTR [rbp-0x158]
   66866:       48 89 85 50 fe ff ff    mov    QWORD PTR [rbp-0x1b0],rax
   6686d:       48 8d 3d ec 2f 08 00    lea    rdi,[rip+0x82fec]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66874:       e8 f7 02 00 00          call   66b70 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x20>
   66879:       48 89 c1                mov    rcx,rax
   6687c:       48 8b 85 50 fe ff ff    mov    rax,QWORD PTR [rbp-0x1b0]
   66883:       31 d2                   xor    edx,edx
   66885:       48 f7 f1                div    rcx
   66888:       48 89 d6                mov    rsi,rdx
   6688b:       48 8d 3d ce 2f 08 00    lea    rdi,[rip+0x82fce]        # e9860 <__cxa_unexpected_handler@@Base+0x58>
   66892:       e8 f9 02 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   66897:       48 8b bd 90 fe ff ff    mov    rdi,QWORD PTR [rbp-0x170]
   6689e:       8a 00                   mov    al,BYTE PTR [rax]
   668a0:       88 85 a2 fe ff ff       mov    BYTE PTR [rbp-0x15e],al
   668a6:       0f b6 85 a3 fe ff ff    movzx  eax,BYTE PTR [rbp-0x15d]
   668ad:       0f b6 8d a2 fe ff ff    movzx  ecx,BYTE PTR [rbp-0x15e]
   668b4:       31 c8                   xor    eax,ecx
   668b6:       33 85 a4 fe ff ff       xor    eax,DWORD PTR [rbp-0x15c]
   668bc:       88 85 5f fe ff ff       mov    BYTE PTR [rbp-0x1a1],al
   668c2:       48 8b b5 a8 fe ff ff    mov    rsi,QWORD PTR [rbp-0x158]
   668c9:       e8 c2 02 00 00          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   668ce:       8a 8d 5f fe ff ff       mov    cl,BYTE PTR [rbp-0x1a1]
   668d4:       88 08                   mov    BYTE PTR [rax],cl
   668d6:       48 8b 85 a8 fe ff ff    mov    rax,QWORD PTR [rbp-0x158]
   668dd:       48 83 c0 01             add    rax,0x1
   668e1:       48 89 85 a8 fe ff ff    mov    QWORD PTR [rbp-0x158],rax
   668e8:       e9 f6 fe ff ff          jmp    667e3 <_Z14generateKeyBufv@@Base+0x423>
   668ed:       48 89 c1                mov    rcx,rax
   668f0:       89 d0                   mov    eax,edx
   668f2:       48 89 8d d8 fe ff ff    mov    QWORD PTR [rbp-0x128],rcx
   668f9:       89 85 d4 fe ff ff       mov    DWORD PTR [rbp-0x12c],eax
   668ff:       e9 9f 00 00 00          jmp    669a3 <_Z14generateKeyBufv@@Base+0x5e3>
   66904:       48 89 c1                mov    rcx,rax
   66907:       89 d0                   mov    eax,edx
   66909:       48 89 8d d8 fe ff ff    mov    QWORD PTR [rbp-0x128],rcx
   66910:       89 85 d4 fe ff ff       mov    DWORD PTR [rbp-0x12c],eax
   66916:       eb 7f                   jmp    66997 <_Z14generateKeyBufv@@Base+0x5d7>
   66918:       48 89 c1                mov    rcx,rax
   6691b:       89 d0                   mov    eax,edx
   6691d:       48 89 8d d8 fe ff ff    mov    QWORD PTR [rbp-0x128],rcx
   66924:       89 85 d4 fe ff ff       mov    DWORD PTR [rbp-0x12c],eax
   6692a:       48 8d bd 20 ff ff ff    lea    rdi,[rbp-0xe0]
   66931:       e8 ea 00 00 00          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   66936:       eb 5f                   jmp    66997 <_Z14generateKeyBufv@@Base+0x5d7>
   66938:       c6 85 b7 fe ff ff 01    mov    BYTE PTR [rbp-0x149],0x1
   6693f:       f6 85 b7 fe ff ff 01    test   BYTE PTR [rbp-0x149],0x1
   66946:       75 0c                   jne    66954 <_Z14generateKeyBufv@@Base+0x594>
   66948:       48 8b bd 90 fe ff ff    mov    rdi,QWORD PTR [rbp-0x170]
   6694f:       e8 cc 00 00 00          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   66954:       48 8d bd 20 ff ff ff    lea    rdi,[rbp-0xe0]
   6695b:       e8 c0 00 00 00          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   66960:       48 8d bd 38 ff ff ff    lea    rdi,[rbp-0xc8]
   66967:       e8 14 0f 07 00          call   d7880 <_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEED1Ev@plt>
   6696c:       48 8d 7d c0             lea    rdi,[rbp-0x40]
   66970:       e8 1b 0f 07 00          call   d7890 <_ZN4SHA1D2Ev@plt>
   66975:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   6697c:       00 00 
   6697e:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   66982:       48 39 c8                cmp    rax,rcx
   66985:       75 51                   jne    669d8 <_Z14generateKeyBufv@@Base+0x618>
   66987:       48 8b 85 98 fe ff ff    mov    rax,QWORD PTR [rbp-0x168]
   6698e:       48 81 c4 c0 01 00 00    add    rsp,0x1c0
   66995:       5d                      pop    rbp
   66996:       c3                      ret
   66997:       48 8d bd 38 ff ff ff    lea    rdi,[rbp-0xc8]
   6699e:       e8 dd 0e 07 00          call   d7880 <_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEED1Ev@plt>
   669a3:       48 8d 7d c0             lea    rdi,[rbp-0x40]
   669a7:       e8 e4 0e 07 00          call   d7890 <_ZN4SHA1D2Ev@plt>
   669ac:       48 8b 85 d8 fe ff ff    mov    rax,QWORD PTR [rbp-0x128]
   669b3:       48 89 85 40 fe ff ff    mov    QWORD PTR [rbp-0x1c0],rax
   669ba:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   669c1:       00 00 
   669c3:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   669c7:       48 39 c8                cmp    rax,rcx
   669ca:       75 0c                   jne    669d8 <_Z14generateKeyBufv@@Base+0x618>
   669cc:       48 8b bd 40 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1c0]
   669d3:       e8 58 ce 06 00          call   d3830 <__emutls_get_address@@Base+0x4d0>
   669d8:       e8 c3 0e 07 00          call   d78a0 <__stack_chk_fail@plt>
   669dd:       cc                      int3
   669de:       cc                      int3
   669df:       cc                      int3
   669e0:       55                      push   rbp
   669e1:       48 89 e5                mov    rbp,rsp
   669e4:       48 83 ec 10             sub    rsp,0x10
   669e8:       48 89 7d f8             mov    QWORD PTR [rbp-0x8],rdi
   669ec:       48 8b 7d f8             mov    rdi,QWORD PTR [rbp-0x8]
   669f0:       48 c7 07 00 00 00 00    mov    QWORD PTR [rdi],0x0
   669f7:       48 c7 47 08 00 00 00    mov    QWORD PTR [rdi+0x8],0x0
   669fe:       00 
   669ff:       48 c7 47 10 00 00 00    mov    QWORD PTR [rdi+0x10],0x0
   66a06:       00 
   66a07:       48 83 c7 10             add    rdi,0x10
   66a0b:       e8 e0 19 00 00          call   683f0 <_ZNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEED2Ev@@Base+0x1b0>
   66a10:       48 83 c4 10             add    rsp,0x10
   66a14:       5d                      pop    rbp
   66a15:       c3                      ret
   66a16:       cc                      int3
   66a17:       cc                      int3
   66a18:       cc                      int3
   66a19:       cc                      int3
   66a1a:       cc                      int3
   66a1b:       cc                      int3
   66a1c:       cc                      int3
   66a1d:       cc                      int3
   66a1e:       cc                      int3
   66a1f:       cc                      int3
   66a20:       55                      push   rbp
   66a21:       48 89 e5                mov    rbp,rsp
   66a24:       48 83 ec 20             sub    rsp,0x20
   66a28:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   66a2f:       00 00 
   66a31:       48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
   66a35:       48 89 7d e8             mov    QWORD PTR [rbp-0x18],rdi
   66a39:       48 8b 75 e8             mov    rsi,QWORD PTR [rbp-0x18]
   66a3d:       48 8d 7d f0             lea    rdi,[rbp-0x10]
   66a41:       e8 da 19 00 00          call   68420 <_ZNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEED2Ev@@Base+0x1e0>
   66a46:       eb 00                   jmp    66a48 <_Z14generateKeyBufv@@Base+0x688>
   66a48:       48 8d 7d f0             lea    rdi,[rbp-0x10]
   66a4c:       e8 ff 19 00 00          call   68450 <_ZNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEED2Ev@@Base+0x210>
   66a51:       eb 00                   jmp    66a53 <_Z14generateKeyBufv@@Base+0x693>
   66a53:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   66a5a:       00 00 
   66a5c:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   66a60:       48 39 c8                cmp    rax,rcx
   66a63:       75 0e                   jne    66a73 <_Z14generateKeyBufv@@Base+0x6b3>
   66a65:       48 83 c4 20             add    rsp,0x20
   66a69:       5d                      pop    rbp
   66a6a:       c3                      ret
   66a6b:       48 89 c7                mov    rdi,rax
   66a6e:       e8 cd 19 00 00          call   68440 <_ZNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEED2Ev@@Base+0x200>
   66a73:       e8 28 0e 07 00          call   d78a0 <__stack_chk_fail@plt>
   66a78:       cc                      int3
   66a79:       cc                      int3
   66a7a:       cc                      int3
   66a7b:       cc                      int3
   66a7c:       cc                      int3
   66a7d:       cc                      int3
   66a7e:       cc                      int3
   66a7f:       cc                      int3

0000000000066a80 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base>:
   66a80:       55                      push   rbp
   66a81:       48 89 e5                mov    rbp,rsp
   66a84:       48 83 ec 60             sub    rsp,0x60
   66a88:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   66a8f:       00 00 
   66a91:       48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
   66a95:       48 89 75 f0             mov    QWORD PTR [rbp-0x10],rsi
   66a99:       48 89 7d d8             mov    QWORD PTR [rbp-0x28],rdi
   66a9d:       48 89 55 d0             mov    QWORD PTR [rbp-0x30],rdx
   66aa1:       48 89 4d c8             mov    QWORD PTR [rbp-0x38],rcx
   66aa5:       48 8b 45 d8             mov    rax,QWORD PTR [rbp-0x28]
   66aa9:       48 89 45 a8             mov    QWORD PTR [rbp-0x58],rax
   66aad:       48 8b 45 f0             mov    rax,QWORD PTR [rbp-0x10]
   66ab1:       48 89 45 e8             mov    QWORD PTR [rbp-0x18],rax
   66ab5:       48 8b 7d d0             mov    rdi,QWORD PTR [rbp-0x30]
   66ab9:       48 89 7d b0             mov    QWORD PTR [rbp-0x50],rdi
   66abd:       48 8b 75 c8             mov    rsi,QWORD PTR [rbp-0x38]
   66ac1:       48 89 75 b8             mov    QWORD PTR [rbp-0x48],rsi
   66ac5:       e8 86 1f 00 00          call   68a50 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE18__insert_with_sizeB8ne210000IPhS5_EENS_11__wrap_iterIS5_EENS6_IPKhEET_T0_l@@Base+0x280>
   66aca:       48 8b 7d a8             mov    rdi,QWORD PTR [rbp-0x58]
   66ace:       48 8b 55 b0             mov    rdx,QWORD PTR [rbp-0x50]
   66ad2:       48 8b 4d b8             mov    rcx,QWORD PTR [rbp-0x48]
   66ad6:       49 89 c0                mov    r8,rax
   66ad9:       48 8b 75 e8             mov    rsi,QWORD PTR [rbp-0x18]
   66add:       e8 ce 0d 07 00          call   d78b0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE18__insert_with_sizeB8ne210000IPhS5_EENS_11__wrap_iterIS5_EENS6_IPKhEET_T0_l@plt>
   66ae2:       48 89 45 e0             mov    QWORD PTR [rbp-0x20],rax
   66ae6:       48 8b 45 e0             mov    rax,QWORD PTR [rbp-0x20]
   66aea:       48 89 45 c0             mov    QWORD PTR [rbp-0x40],rax
   66aee:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   66af5:       00 00 
   66af7:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   66afb:       48 39 c8                cmp    rax,rcx
   66afe:       75 0a                   jne    66b0a <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x8a>
   66b00:       48 8b 45 c0             mov    rax,QWORD PTR [rbp-0x40]
   66b04:       48 83 c4 60             add    rsp,0x60
   66b08:       5d                      pop    rbp
   66b09:       c3                      ret
   66b0a:       e8 91 0d 07 00          call   d78a0 <__stack_chk_fail@plt>
   66b0f:       cc                      int3
   66b10:       55                      push   rbp
   66b11:       48 89 e5                mov    rbp,rsp
   66b14:       48 83 ec 20             sub    rsp,0x20
   66b18:       48 89 7d f0             mov    QWORD PTR [rbp-0x10],rdi
   66b1c:       48 8b 45 f0             mov    rax,QWORD PTR [rbp-0x10]
   66b20:       48 89 45 e8             mov    QWORD PTR [rbp-0x18],rax
   66b24:       48 8b 78 08             mov    rdi,QWORD PTR [rax+0x8]
   66b28:       e8 93 0d 07 00          call   d78c0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE26__add_alignment_assumptionB8ne210000IPhTnNS_9enable_ifIXsr10is_pointerIT_EE5valueEiE4typeELi0EEES5_S7_@plt>
   66b2d:       48 8b 7d e8             mov    rdi,QWORD PTR [rbp-0x18]
   66b31:       48 89 c6                mov    rsi,rax
   66b34:       e8 07 1c 00 00          call   68740 <_ZNSt6__ndk116allocator_traitsINS_9allocatorIhEEE7destroyB8ne210000IhTnNS_9enable_ifIXsr13__has_destroyIS2_PT_EE5valueEiE4typeELi0EEEvRS2_S7_@@Base+0x160>
   66b39:       48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
   66b3d:       48 8b 45 f8             mov    rax,QWORD PTR [rbp-0x8]
   66b41:       48 83 c4 20             add    rsp,0x20
   66b45:       5d                      pop    rbp
   66b46:       c3                      ret
   66b47:       cc                      int3
   66b48:       cc                      int3
   66b49:       cc                      int3
   66b4a:       cc                      int3
   66b4b:       cc                      int3
   66b4c:       cc                      int3
   66b4d:       cc                      int3
   66b4e:       cc                      int3
   66b4f:       cc                      int3
--
   6710d:       e8 de 06 07 00          call   d77f0 <_Z14generateKeyBufv@plt>
   67112:       48 8d bd e0 fe ff ff    lea    rdi,[rbp-0x120]
   67119:       e8 52 02 00 00          call   67370 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x290>
   6711e:       eb 00                   jmp    67120 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x40>
   67120:       48 8d bd f0 fe ff ff    lea    rdi,[rbp-0x110]
   67127:       48 8d 35 a2 03 00 00    lea    rsi,[rip+0x3a2]        # 674d0 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x70>
   6712e:       e8 6d 03 00 00          call   674a0 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x40>
   67133:       48 89 85 58 fe ff ff    mov    QWORD PTR [rbp-0x1a8],rax
   6713a:       eb 00                   jmp    6713c <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x5c>
   6713c:       bf 30 00 00 00          mov    edi,0x30
   67141:       e8 ba 03 00 00          call   67500 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0xa0>
   67146:       88 85 57 fe ff ff       mov    BYTE PTR [rbp-0x1a9],al
   6714c:       eb 00                   jmp    6714e <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x6e>
   6714e:       48 8b bd 58 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1a8]
   67155:       8a 85 57 fe ff ff       mov    al,BYTE PTR [rbp-0x1a9]
   6715b:       88 85 c7 fe ff ff       mov    BYTE PTR [rbp-0x139],al
   67161:       48 8d b5 c7 fe ff ff    lea    rsi,[rbp-0x139]
   67168:       e8 93 07 07 00          call   d7900 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@plt>
   6716d:       eb 00                   jmp    6716f <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x8f>
   6716f:       48 8d 85 c8 fe ff ff    lea    rax,[rbp-0x138]
   67176:       48 89 85 68 fe ff ff    mov    QWORD PTR [rbp-0x198],rax
   6717d:       48 8b bd 68 fe ff ff    mov    rdi,QWORD PTR [rbp-0x198]
   67184:       e8 c7 03 00 00          call   67550 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0xf0>
   67189:       48 89 85 b8 fe ff ff    mov    QWORD PTR [rbp-0x148],rax
   67190:       48 8b bd 68 fe ff ff    mov    rdi,QWORD PTR [rbp-0x198]
   67197:       e8 74 f9 ff ff          call   66b10 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x90>
   6719c:       48 89 85 b0 fe ff ff    mov    QWORD PTR [rbp-0x150],rax
   671a3:       48 8d bd b8 fe ff ff    lea    rdi,[rbp-0x148]
   671aa:       48 8d b5 b0 fe ff ff    lea    rsi,[rbp-0x150]
   671b1:       e8 da 03 00 00          call   67590 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x130>
   671b6:       a8 01                   test   al,0x1
   671b8:       75 05                   jne    671bf <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0xdf>
   671ba:       e9 b2 00 00 00          jmp    67271 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x191>
   671bf:       48 8d bd b8 fe ff ff    lea    rdi,[rbp-0x148]
   671c6:       e8 f5 03 00 00          call   675c0 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x160>
   671cb:       8a 00                   mov    al,BYTE PTR [rax]
   671cd:       88 85 67 fe ff ff       mov    BYTE PTR [rbp-0x199],al
   671d3:       48 8d 85 f0 fe ff ff    lea    rax,[rbp-0x110]
   671da:       48 89 85 48 fe ff ff    mov    QWORD PTR [rbp-0x1b8],rax
   671e1:       bf 02 00 00 00          mov    edi,0x2
   671e6:       e8 25 04 00 00          call   67610 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x1b0>
   671eb:       89 85 50 fe ff ff       mov    DWORD PTR [rbp-0x1b0],eax
   671f1:       eb 00                   jmp    671f3 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x113>
   671f3:       48 8b bd 48 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1b8]
   671fa:       8b 85 50 fe ff ff       mov    eax,DWORD PTR [rbp-0x1b0]
   67200:       89 85 ac fe ff ff       mov    DWORD PTR [rbp-0x154],eax
   67206:       48 8d b5 ac fe ff ff    lea    rsi,[rbp-0x154]
   6720d:       e8 be 03 00 00          call   675d0 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x170>
   67212:       48 89 85 40 fe ff ff    mov    QWORD PTR [rbp-0x1c0],rax
   67219:       eb 00                   jmp    6721b <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x13b>
   6721b:       48 8b bd 40 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1c0]
   67222:       0f b6 b5 67 fe ff ff    movzx  esi,BYTE PTR [rbp-0x199]
   67229:       e8 e2 06 07 00          call   d7910 <_ZNSt6__ndk113basic_ostreamIcNS_11char_traitsIcEEElsEi@plt>
   6722e:       eb 00                   jmp    67230 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x150>
   67230:       eb 00                   jmp    67232 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x152>
   67232:       48 8d bd b8 fe ff ff    lea    rdi,[rbp-0x148]
   67239:       e8 22 04 00 00          call   67660 <_ZNSt6__ndk1lsB8ne210000INS_11char_traitsIcEEEERNS_13basic_ostreamIcT_EES6_RKNS_8__iom_t4IcEE@@Base+0x200>
   6723e:       e9 60 ff ff ff          jmp    671a3 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0xc3>
   67243:       48 89 c1                mov    rcx,rax
   67246:       89 d0                   mov    eax,edx
   67248:       48 89 8d 78 fe ff ff    mov    QWORD PTR [rbp-0x188],rcx
   6724f:       89 85 74 fe ff ff       mov    DWORD PTR [rbp-0x18c],eax
   67255:       e9 ce 00 00 00          jmp    67328 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x248>
   6725a:       48 89 c1                mov    rcx,rax
   6725d:       89 d0                   mov    eax,edx
   6725f:       48 89 8d 78 fe ff ff    mov    QWORD PTR [rbp-0x188],rcx
   67266:       89 85 74 fe ff ff       mov    DWORD PTR [rbp-0x18c],eax
   6726c:       e9 ab 00 00 00          jmp    6731c <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x23c>
   67271:       48 8b 85 88 fe ff ff    mov    rax,QWORD PTR [rbp-0x178]
   67278:       48 89 85 38 fe ff ff    mov    QWORD PTR [rbp-0x1c8],rax
   6727f:       48 8d bd 90 fe ff ff    lea    rdi,[rbp-0x170]
   67286:       48 8d b5 e0 fe ff ff    lea    rsi,[rbp-0x120]
   6728d:       e8 1e 04 00 00          call   676b0 <_ZN7_JNIEnv12NewStringUTFEPKc@@Base+0x30>
   67292:       eb 00                   jmp    67294 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x1b4>
   67294:       48 8d bd 90 fe ff ff    lea    rdi,[rbp-0x170]
   6729b:       e8 40 04 00 00          call   676e0 <_ZN7_JNIEnv12NewStringUTFEPKc@@Base+0x60>
   672a0:       48 8b bd 38 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1c8]
   672a7:       48 89 c6                mov    rsi,rax
   672aa:       e8 71 06 07 00          call   d7920 <_ZN7_JNIEnv12NewStringUTFEPKc@plt>
   672af:       48 89 85 30 fe ff ff    mov    QWORD PTR [rbp-0x1d0],rax
   672b6:       eb 00                   jmp    672b8 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x1d8>
--
   672d7:       e8 44 f7 ff ff          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   672dc:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   672e3:       00 00 
   672e5:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   672e9:       48 39 c8                cmp    rax,rcx
   672ec:       75 72                   jne    67360 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x280>
   672ee:       48 8b 85 30 fe ff ff    mov    rax,QWORD PTR [rbp-0x1d0]
   672f5:       48 81 c4 e0 01 00 00    add    rsp,0x1e0
   672fc:       5d                      pop    rbp
   672fd:       c3                      ret
   672fe:       48 89 c1                mov    rcx,rax
   67301:       89 d0                   mov    eax,edx
   67303:       48 89 8d 78 fe ff ff    mov    QWORD PTR [rbp-0x188],rcx
   6730a:       89 85 74 fe ff ff       mov    DWORD PTR [rbp-0x18c],eax
   67310:       48 8d bd 90 fe ff ff    lea    rdi,[rbp-0x170]
   67317:       e8 64 05 07 00          call   d7880 <_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEED1Ev@plt>
   6731c:       48 8d bd e0 fe ff ff    lea    rdi,[rbp-0x120]
   67323:       e8 d8 03 00 00          call   67700 <_ZN7_JNIEnv12NewStringUTFEPKc@@Base+0x80>
   67328:       48 8d bd c8 fe ff ff    lea    rdi,[rbp-0x138]
   6732f:       e8 ec f6 ff ff          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   67334:       48 8b 85 78 fe ff ff    mov    rax,QWORD PTR [rbp-0x188]
   6733b:       48 89 85 28 fe ff ff    mov    QWORD PTR [rbp-0x1d8],rax
   67342:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   67349:       00 00 
   6734b:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   6734f:       48 39 c8                cmp    rax,rcx
   67352:       75 0c                   jne    67360 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x280>
   67354:       48 8b bd 28 fe ff ff    mov    rdi,QWORD PTR [rbp-0x1d8]
   6735b:       e8 d0 c4 06 00          call   d3830 <__emutls_get_address@@Base+0x4d0>
   67360:       e8 3b 05 07 00          call   d78a0 <__stack_chk_fail@plt>
   67365:       cc                      int3
   67366:       cc                      int3
   67367:       cc                      int3
   67368:       cc                      int3
   67369:       cc                      int3
   6736a:       cc                      int3
   6736b:       cc                      int3
   6736c:       cc                      int3
   6736d:       cc                      int3
   6736e:       cc                      int3
   6736f:       cc                      int3
   67370:       55                      push   rbp
   67371:       48 89 e5                mov    rbp,rsp
   67374:       48 83 ec 20             sub    rsp,0x20
   67378:       48 89 7d f8             mov    QWORD PTR [rbp-0x8],rdi
   6737c:       48 8b 7d f8             mov    rdi,QWORD PTR [rbp-0x8]
   67380:       48 89 7d e0             mov    QWORD PTR [rbp-0x20],rdi
   67384:       48 83 ef 80             sub    rdi,0xffffffffffffff80
   67388:       e8 f3 3d 00 00          call   6b180 <_ZNSt6__ndk19allocatorIhE9constructB8ne210000IhJEEEvPT_DpOT0_@@Base+0x20>
   6738d:       48 8b 7d e0             mov    rdi,QWORD PTR [rbp-0x20]
   67391:       48 8b 05 a8 d1 07 00    mov    rax,QWORD PTR [rip+0x7d1a8]        # e4540 <_ZTVNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEEE@@Base+0x6c20>
   67398:       48 89 c1                mov    rcx,rax
   6739b:       48 83 c1 18             add    rcx,0x18
   6739f:       48 89 0f                mov    QWORD PTR [rdi],rcx
   673a2:       48 89 c1                mov    rcx,rax
   673a5:       48 83 c1 68             add    rcx,0x68
   673a9:       48 89 8f 80 00 00 00    mov    QWORD PTR [rdi+0x80],rcx
   673b0:       48 83 c0 40             add    rax,0x40
   673b4:       48 89 47 10             mov    QWORD PTR [rdi+0x10],rax
   673b8:       48 89 fa                mov    rdx,rdi
   673bb:       48 83 c2 18             add    rdx,0x18
   673bf:       48 8b 35 82 d1 07 00    mov    rsi,QWORD PTR [rip+0x7d182]        # e4548 <_ZTTNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEEE@@Base+0x6bb0>
   673c6:       48 83 c6 08             add    rsi,0x8
   673ca:       e8 f1 3d 00 00          call   6b1c0 <_ZNSt6__ndk19allocatorIhE9constructB8ne210000IhJEEEvPT_DpOT0_@@Base+0x60>
   673cf:       eb 00                   jmp    673d1 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x2f1>
   673d1:       48 8b 7d e0             mov    rdi,QWORD PTR [rbp-0x20]
   673d5:       48 8b 05 64 d1 07 00    mov    rax,QWORD PTR [rip+0x7d164]        # e4540 <_ZTVNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEEE@@Base+0x6c20>
   673dc:       48 89 c1                mov    rcx,rax
   673df:       48 83 c1 18             add    rcx,0x18
   673e3:       48 89 0f                mov    QWORD PTR [rdi],rcx
   673e6:       48 89 c1                mov    rcx,rax
   673e9:       48 83 c1 68             add    rcx,0x68
   673ed:       48 89 8f 80 00 00 00    mov    QWORD PTR [rdi+0x80],rcx
   673f4:       48 83 c0 40             add    rax,0x40
   673f8:       48 89 47 10             mov    QWORD PTR [rdi+0x10],rax
   673fc:       48 83 c7 18             add    rdi,0x18
   67400:       be 18 00 00 00          mov    esi,0x18
   67405:       e8 56 3e 00 00          call   6b260 <_ZNSt6__ndk19allocatorIhE9constructB8ne210000IhJEEEvPT_DpOT0_@@Base+0x100>
   6740a:       eb 00                   jmp    6740c <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x32c>
   6740c:       48 83 c4 20             add    rsp,0x20
   67410:       5d                      pop    rbp
   67411:       c3                      ret
   67412:       48 89 c1                mov    rcx,rax
   67415:       89 d0                   mov    eax,edx
   67417:       48 89 4d f0             mov    QWORD PTR [rbp-0x10],rcx
   6741b:       89 45 ec                mov    DWORD PTR [rbp-0x14],eax
   6741e:       eb 20                   jmp    67440 <Java_com_example_myapk_ImageEncryptor_getEncryptionKey@@Base+0x360>
   67420:       48 8b 7d e0             mov    rdi,QWORD PTR [rbp-0x20]
   67424:       48 89 c1                mov    rcx,rax
   67427:       89 d0                   mov    eax,edx
   67429:       48 89 4d f0             mov    QWORD PTR [rbp-0x10],rcx
   6742d:       89 45 ec                mov    DWORD PTR [rbp-0x14],eax
   67430:       48 8b 35 11 d1 07 00    mov    rsi,QWORD PTR [rip+0x7d111]        # e4548 <_ZTTNSt6__ndk118basic_stringstreamIcNS_11char_traitsIcEENS_9allocatorIcEEEE@@Base+0x6bb0>
   67437:       48 83 c6 08             add    rsi,0x8
   6743b:       e8 f0 04 07 00          call   d7930 <_ZNSt6__ndk114basic_iostreamIcNS_11char_traitsIcEEED2Ev@plt>
   67440:       48 8b 7d e0             mov    rdi,QWORD PTR [rbp-0x20]
   67444:       48 81 c7 80 00 00 00    add    rdi,0x80
   6744b:       e8 f0 04 07 00          call   d7940 <_ZNSt6__ndk19basic_iosIcNS_11char_traitsIcEEED2Ev@plt>
   67450:       48 8b 7d f0             mov    rdi,QWORD PTR [rbp-0x10]
   67454:       e8 d7 c3 06 00          call   d3830 <__emutls_get_address@@Base+0x4d0>
--
   6778d:       e8 5e 00 07 00          call   d77f0 <_Z14generateKeyBufv@plt>
   67792:       48 8b 7d d8             mov    rdi,QWORD PTR [rbp-0x28]
   67796:       8b 75 bc                mov    esi,DWORD PTR [rbp-0x44]
   67799:       e8 f2 01 07 00          call   d7990 <_ZN7_JNIEnv12NewByteArrayEi@plt>
   6779e:       48 89 45 88             mov    QWORD PTR [rbp-0x78],rax
   677a2:       eb 00                   jmp    677a4 <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x64>
   677a4:       48 8b 45 88             mov    rax,QWORD PTR [rbp-0x78]
   677a8:       48 89 45 b0             mov    QWORD PTR [rbp-0x50],rax
   677ac:       48 63 7d bc             movsxd rdi,DWORD PTR [rbp-0x44]
   677b0:       e8 eb 01 07 00          call   d79a0 <_Znam@plt>
   677b5:       48 89 45 80             mov    QWORD PTR [rbp-0x80],rax
   677b9:       eb 00                   jmp    677bb <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x7b>
   677bb:       48 8b 45 80             mov    rax,QWORD PTR [rbp-0x80]
   677bf:       48 89 45 98             mov    QWORD PTR [rbp-0x68],rax
   677c3:       c7 45 94 00 00 00 00    mov    DWORD PTR [rbp-0x6c],0x0
   677ca:       8b 45 94                mov    eax,DWORD PTR [rbp-0x6c]
   677cd:       3b 45 bc                cmp    eax,DWORD PTR [rbp-0x44]
   677d0:       0f 8d 81 00 00 00       jge    67857 <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x117>
   677d6:       48 8b 45 c0             mov    rax,QWORD PTR [rbp-0x40]
   677da:       48 63 4d 94             movsxd rcx,DWORD PTR [rbp-0x6c]
   677de:       0f be 04 08             movsx  eax,BYTE PTR [rax+rcx*1]
   677e2:       89 85 7c ff ff ff       mov    DWORD PTR [rbp-0x84],eax
   677e8:       48 63 45 94             movsxd rax,DWORD PTR [rbp-0x6c]
   677ec:       48 89 85 70 ff ff ff    mov    QWORD PTR [rbp-0x90],rax
   677f3:       48 8d 7d e0             lea    rdi,[rbp-0x20]
   677f7:       e8 74 f3 ff ff          call   66b70 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x20>
   677fc:       48 89 c1                mov    rcx,rax
   677ff:       48 8b 85 70 ff ff ff    mov    rax,QWORD PTR [rbp-0x90]
   67806:       31 d2                   xor    edx,edx
   67808:       48 f7 f1                div    rcx
   6780b:       48 89 d6                mov    rsi,rdx
   6780e:       48 8d 7d e0             lea    rdi,[rbp-0x20]
   67812:       e8 79 f3 ff ff          call   66b90 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x40>
   67817:       48 89 c1                mov    rcx,rax
   6781a:       8b 85 7c ff ff ff       mov    eax,DWORD PTR [rbp-0x84]
   67820:       0f b6 09                movzx  ecx,BYTE PTR [rcx]
   67823:       31 c8                   xor    eax,ecx
   67825:       88 c2                   mov    dl,al
   67827:       48 8b 45 98             mov    rax,QWORD PTR [rbp-0x68]
   6782b:       48 63 4d 94             movsxd rcx,DWORD PTR [rbp-0x6c]
   6782f:       88 14 08                mov    BYTE PTR [rax+rcx*1],dl
   67832:       8b 45 94                mov    eax,DWORD PTR [rbp-0x6c]
   67835:       83 c0 01                add    eax,0x1
   67838:       89 45 94                mov    DWORD PTR [rbp-0x6c],eax
   6783b:       eb 8d                   jmp    677ca <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x8a>
   6783d:       48 89 c1                mov    rcx,rax
   67840:       89 d0                   mov    eax,edx
   67842:       48 89 4d a8             mov    QWORD PTR [rbp-0x58],rcx
   67846:       89 45 a4                mov    DWORD PTR [rbp-0x5c],eax
   67849:       48 8d 7d e0             lea    rdi,[rbp-0x20]
   6784d:       e8 ce f1 ff ff          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   67852:       e9 83 00 00 00          jmp    678da <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x19a>
   67857:       48 8b 7d d8             mov    rdi,QWORD PTR [rbp-0x28]
   6785b:       48 8b 75 b0             mov    rsi,QWORD PTR [rbp-0x50]
   6785f:       8b 4d bc                mov    ecx,DWORD PTR [rbp-0x44]
   67862:       4c 8b 45 98             mov    r8,QWORD PTR [rbp-0x68]
   67866:       31 d2                   xor    edx,edx
   67868:       e8 43 01 07 00          call   d79b0 <_ZN7_JNIEnv18SetByteArrayRegionEP11_jbyteArrayiiPKa@plt>
   6786d:       eb 00                   jmp    6786f <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x12f>
   6786f:       48 8b 45 98             mov    rax,QWORD PTR [rbp-0x68]
   67873:       48 89 85 68 ff ff ff    mov    QWORD PTR [rbp-0x98],rax
   6787a:       48 83 f8 00             cmp    rax,0x0
   6787e:       74 0c                   je     6788c <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x14c>
   67880:       48 8b bd 68 ff ff ff    mov    rdi,QWORD PTR [rbp-0x98]
   67887:       e8 34 01 07 00          call   d79c0 <_ZdaPv@plt>
   6788c:       48 8b 7d d8             mov    rdi,QWORD PTR [rbp-0x28]
   67890:       48 8b 75 c8             mov    rsi,QWORD PTR [rbp-0x38]
   67894:       48 8b 55 c0             mov    rdx,QWORD PTR [rbp-0x40]
   67898:       b9 02 00 00 00          mov    ecx,0x2
   6789d:       e8 2e 01 07 00          call   d79d0 <_ZN7_JNIEnv24ReleaseByteArrayElementsEP11_jbyteArrayPai@plt>
   678a2:       eb 00                   jmp    678a4 <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x164>
   678a4:       48 8b 45 b0             mov    rax,QWORD PTR [rbp-0x50]
   678a8:       48 89 85 60 ff ff ff    mov    QWORD PTR [rbp-0xa0],rax
   678af:       48 8d 7d e0             lea    rdi,[rbp-0x20]
   678b3:       e8 68 f1 ff ff          call   66a20 <_Z14generateKeyBufv@@Base+0x660>
   678b8:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   678bf:       00 00 
   678c1:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   678c5:       48 39 c8                cmp    rax,rcx
   678c8:       75 39                   jne    67903 <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x1c3>
   678ca:       48 8b 85 60 ff ff ff    mov    rax,QWORD PTR [rbp-0xa0]
   678d1:       48 81 c4 b0 00 00 00    add    rsp,0xb0
   678d8:       5d                      pop    rbp
   678d9:       c3                      ret
   678da:       48 8b 45 a8             mov    rax,QWORD PTR [rbp-0x58]
   678de:       48 89 85 58 ff ff ff    mov    QWORD PTR [rbp-0xa8],rax
   678e5:       64 48 8b 04 25 28 00    mov    rax,QWORD PTR fs:0x28
   678ec:       00 00 
   678ee:       48 8b 4d f8             mov    rcx,QWORD PTR [rbp-0x8]
   678f2:       48 39 c8                cmp    rax,rcx
   678f5:       75 0c                   jne    67903 <Java_com_example_myapk_ImageEncryptor_encryptDataNative@@Base+0x1c3>
   678f7:       48 8b bd 58 ff ff ff    mov    rdi,QWORD PTR [rbp-0xa8]
   678fe:       e8 2d bf 06 00          call   d3830 <__emutls_get_address@@Base+0x4d0>
   67903:       e8 98 ff 06 00          call   d78a0 <__stack_chk_fail@plt>
   67908:       cc                      int3
   67909:       cc                      int3
   6790a:       cc                      int3
   6790b:       cc                      int3
   6790c:       cc                      int3
   6790d:       cc                      int3
   6790e:       cc                      int3
   6790f:       cc                      int3

0000000000067910 <_ZN7_JNIEnv20GetByteArrayElementsEP11_jbyteArrayPh@@Base>:
   67910:       55                      push   rbp
   67911:       48 89 e5                mov    rbp,rsp
   67914:       48 83 ec 20             sub    rsp,0x20
   67918:       48 89 7d f8             mov    QWORD PTR [rbp-0x8],rdi
   6791c:       48 89 75 f0             mov    QWORD PTR [rbp-0x10],rsi
   67920:       48 89 55 e8             mov    QWORD PTR [rbp-0x18],rdx
   67924:       48 8b 7d f8             mov    rdi,QWORD PTR [rbp-0x8]
   67928:       48 8b 07                mov    rax,QWORD PTR [rdi]
   6792b:       48 8b 80 c0 05 00 00    mov    rax,QWORD PTR [rax+0x5c0]
   67932:       48 8b 75 f0             mov    rsi,QWORD PTR [rbp-0x10]
   67936:       48 8b 55 e8             mov    rdx,QWORD PTR [rbp-0x18]
   6793a:       ff d0                   call   rax
   6793c:       48 83 c4 20             add    rsp,0x20
   67940:       5d                      pop    rbp
   67941:       c3                      ret
   67942:       cc                      int3
   67943:       cc                      int3
   67944:       cc                      int3
   67945:       cc                      int3
   67946:       cc                      int3
   67947:       cc                      int3
   67948:       cc                      int3
   67949:       cc                      int3
   6794a:       cc                      int3
   6794b:       cc                      int3
   6794c:       cc                      int3
   6794d:       cc                      int3
   6794e:       cc                      int3
   6794f:       cc                      int3

0000000000067950 <_ZN7_JNIEnv14GetArrayLengthEP7_jarray@@Base>:
   67950:       55                      push   rbp
   67951:       48 89 e5                mov    rbp,rsp
   67954:       48 83 ec 10             sub    rsp,0x10
   67958:       48 89 7d f8             mov    QWORD PTR [rbp-0x8],rdi
   6795c:       48 89 75 f0             mov    QWORD PTR [rbp-0x10],rsi
   67960:       48 8b 7d f8             mov    rdi,QWORD PTR [rbp-0x8]
   67964:       48 8b 07                mov    rax,QWORD PTR [rdi]
   67967:       48 8b 80 58 05 00 00    mov    rax,QWORD PTR [rax+0x558]
   6796e:       48 8b 75 f0             mov    rsi,QWORD PTR [rbp-0x10]
   67972:       ff d0                   call   rax
   67974:       48 83 c4 10             add    rsp,0x10
   67978:       5d                      pop    rbp
   67979:       c3                      ret
   6797a:       cc                      int3
   6797b:       cc                      int3
   6797c:       cc                      int3
   6797d:       cc                      int3
   6797e:       cc                      int3
   6797f:       cc                      int3

--
00000000000d77f0 <_Z14generateKeyBufv@plt>:
   d77f0:       ff 25 4a d2 00 00       jmp    QWORD PTR [rip+0xd24a]        # e4a40 <_Z14generateKeyBufv@@Base+0x7e680>
   d77f6:       68 02 00 00 00          push   0x2
   d77fb:       e9 c0 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7800 <__cxa_guard_acquire@plt>:
   d7800:       ff 25 42 d2 00 00       jmp    QWORD PTR [rip+0xd242]        # e4a48 <__cxa_guard_acquire@@Base+0x2fbdc>
   d7806:       68 03 00 00 00          push   0x3
   d780b:       e9 b0 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7810 <__cxa_guard_release@plt>:
   d7810:       ff 25 3a d2 00 00       jmp    QWORD PTR [rip+0xd23a]        # e4a50 <__cxa_guard_release@@Base+0x2faac>
   d7816:       68 04 00 00 00          push   0x4
   d781b:       e9 a0 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7820 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@plt>:
   d7820:       ff 25 32 d2 00 00       jmp    QWORD PTR [rip+0xd232]        # e4a58 <_ZNSt6__ndk111__wrap_iterIPKhEC2B8ne210000IPhTnNS_9enable_ifIXsr4_AndINS_14is_convertibleIRKT_S2_EENS_7_OrImplIXaantcvbsr7is_sameIRS1_NS_15iterator_traitsIS8_E9referenceEEE5valuenesZT1_Li0EEE7_ResultINS_7is_sameISD_SG_EENSJ_ISD_RKu20__remove_reference_tISG_EEEEEEE5valueEiE4typeELi0EEERKNS0_IS8_EE@@Base+0x7df08>
   d7826:       68 05 00 00 00          push   0x5
   d782b:       e9 90 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7830 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@plt>:
   d7830:       ff 25 2a d2 00 00       jmp    QWORD PTR [rip+0xd22a]        # e4a60 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE6insertB8ne210000IPhTnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS7_E9referenceEEE5valueEiE4typeELi0EEENS_11__wrap_iterIS5_EENSD_IPKhEES7_S7_@@Base+0x7dfe0>
   d7836:       68 06 00 00 00          push   0x6
   d783b:       e9 80 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7840 <_ZN4SHA1C2Ev@plt>:
   d7840:       ff 25 22 d2 00 00       jmp    QWORD PTR [rip+0xd222]        # e4a68 <_ZN4SHA1C2Ev@@Base+0x7de68>
   d7846:       68 07 00 00 00          push   0x7
   d784b:       e9 70 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7850 <_ZN4SHA16updateEPKvm@plt>:
   d7850:       ff 25 1a d2 00 00       jmp    QWORD PTR [rip+0xd21a]        # e4a70 <_ZN4SHA16updateEPKvm@@Base+0x7de20>
   d7856:       68 08 00 00 00          push   0x8
   d785b:       e9 60 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7860 <_ZN4SHA15finalEv@plt>:
   d7860:       ff 25 12 d2 00 00       jmp    QWORD PTR [rip+0xd212]        # e4a78 <_ZN4SHA15finalEv@@Base+0x7dd88>
   d7866:       68 09 00 00 00          push   0x9
   d786b:       e9 50 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7870 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEEC2B8ne210000INS_11__wrap_iterIPcEETnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS9_E9referenceEEE5valueEiE4typeELi0EEES9_S9_@plt>:
   d7870:       ff 25 0a d2 00 00       jmp    QWORD PTR [rip+0xd20a]        # e4a80 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEEC2B8ne210000INS_11__wrap_iterIPcEETnNS_9enable_ifIXaasr31__has_forward_iterator_categoryIT_EE5valuesr16is_constructibleIhNS_15iterator_traitsIS9_E9referenceEEE5valueEiE4typeELi0EEES9_S9_@@Base+0x7db70>
   d7876:       68 0a 00 00 00          push   0xa
   d787b:       e9 40 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7880 <_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEED1Ev@plt>:
   d7880:       ff 25 02 d2 00 00       jmp    QWORD PTR [rip+0xd202]        # e4a88 <_ZNSt6__ndk112basic_stringIcNS_11char_traitsIcEENS_9allocatorIcEEED1Ev@@Base+0x78798>
   d7886:       68 0b 00 00 00          push   0xb
   d788b:       e9 30 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d7890 <_ZN4SHA1D2Ev@plt>:
   d7890:       ff 25 fa d1 00 00       jmp    QWORD PTR [rip+0xd1fa]        # e4a90 <_ZN4SHA1D2Ev@@Base+0x7d9d0>
   d7896:       68 0c 00 00 00          push   0xc
   d789b:       e9 20 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78a0 <__stack_chk_fail@plt>:
   d78a0:       ff 25 f2 d1 00 00       jmp    QWORD PTR [rip+0xd1f2]        # e4a98 <__stack_chk_fail@LIBC>
   d78a6:       68 0d 00 00 00          push   0xd
   d78ab:       e9 10 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78b0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE18__insert_with_sizeB8ne210000IPhS5_EENS_11__wrap_iterIS5_EENS6_IPKhEET_T0_l@plt>:
   d78b0:       ff 25 ea d1 00 00       jmp    QWORD PTR [rip+0xd1ea]        # e4aa0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE18__insert_with_sizeB8ne210000IPhS5_EENS_11__wrap_iterIS5_EENS6_IPKhEET_T0_l@@Base+0x7c2d0>
   d78b6:       68 0e 00 00 00          push   0xe
   d78bb:       e9 00 ff ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78c0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE26__add_alignment_assumptionB8ne210000IPhTnNS_9enable_ifIXsr10is_pointerIT_EE5valueEiE4typeELi0EEES5_S7_@plt>:
   d78c0:       ff 25 e2 d1 00 00       jmp    QWORD PTR [rip+0xd1e2]        # e4aa8 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE26__add_alignment_assumptionB8ne210000IPhTnNS_9enable_ifIXsr10is_pointerIT_EE5valueEiE4typeELi0EEES5_S7_@@Base+0x7c308>
   d78c6:       68 0f 00 00 00          push   0xf
   d78cb:       e9 f0 fe ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78d0 <_ZN4SHA15resetEv@plt>:
   d78d0:       ff 25 da d1 00 00       jmp    QWORD PTR [rip+0xd1da]        # e4ab0 <_ZN4SHA15resetEv@@Base+0x7d040>
   d78d6:       68 10 00 00 00          push   0x10
   d78db:       e9 e0 fe ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78e0 <_ZN4SHA19transformEPKh@plt>:
   d78e0:       ff 25 d2 d1 00 00       jmp    QWORD PTR [rip+0xd1d2]        # e4ab8 <_ZN4SHA19transformEPKh@@Base+0x7cef8>
   d78e6:       68 11 00 00 00          push   0x11
   d78eb:       e9 d0 fe ff ff          jmp    d77c0 <_ZnamSt11align_val_t@@Base+0x10>

00000000000d78f0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE16__init_with_sizeB8ne210000INS_11__wrap_iterIPcEES7_EEvT_T0_m@plt>:
   d78f0:       ff 25 ca d1 00 00       jmp    QWORD PTR [rip+0xd1ca]        # e4ac0 <_ZNSt6__ndk16vectorIhNS_9allocatorIhEEE16__init_with_sizeB8ne210000INS_11__wrap_iterIPcEES7_EEvT_T0_m@@Base+0x7a720>

```

## Phase 6: The Known-Plaintext Attack (KPA)

We now know that `background.bkp` is simply `hidden_flag.jpg` encrypted with a 32-byte repeating XOR key. Because both files are standard JPEGs, their first 32 bytes (the file headers) are identical.

By XORing the first 32 bytes of the plaintext decoy image against the encrypted backup, we can extract the true 32-byte C++ key and use it to decrypt the entire file, revealing the final image.

```jsx
# Read the first 32 bytes of the plain JPEG header
with open('../hidden_flag.jpg', 'rb') as f1:
    plain = f1.read(32)
    
# Read the encrypted target file
with open('../chall_decompiled/assets/background.bkp', 'rb') as f2:
    cipher = f2.read()

# 1. Recover the 32-byte key via Known-Plaintext Attack (Plaintext ^ Ciphertext = Key)
key = bytearray()
for i in range(32):
    key.append(plain[i] ^ cipher[i])

print(f"[*] Recovered 32-byte Key: {[hex(k) for k in key]}")

# 2. Decrypt the entire 297KB image using the recovered key
decrypted = bytearray()
for i in range(len(cipher)):
    decrypted.append(cipher[i] ^ key[i % 32])

# 3. Save the final unencrypted image
with open('FINAL_FLAG.jpg', 'wb') as f:
    f.write(decrypted)

print("[+] Decryption absolute success! Saved as FINAL_FLAG.jpg")
```

<img width="774" height="629" alt="image" src="https://github.com/user-attachments/assets/4a79ee06-46f9-4333-87d2-c6298c7458d9" />

<img width="1509" height="864" alt="image" src="https://github.com/user-attachments/assets/88ab9626-1e88-4dd4-bfcd-6c72e507b9de" />

### **Final Flag:**

**`hack10{t3r_ez_X0r}`**
