<img width="499" height="510" alt="image" src="https://github.com/user-attachments/assets/490d469f-0fa5-4eb8-bb5c-ad99d62cb55c" />


<img width="908" height="340" alt="image" src="https://github.com/user-attachments/assets/821a3b2b-f023-436c-b0a9-2151b2db67fc" />


i use strings command to check the pdf 

then i notice a long encryption of base64

<img width="899" height="644" alt="image" src="https://github.com/user-attachments/assets/d9fe9f3e-b48b-4a56-ac8e-0a85b7823b4b" />

then i try use cyberchef to decode it

<img width="1033" height="596" alt="image" src="https://github.com/user-attachments/assets/0d88f007-d51e-4de1-ab50-6a43ada9afcb" />

After decoding the Base64 blob, I saved the raw binary output rather than the `magic` classification. The raw file is the actual Portable Executable artifact, which allows reproducible analysis (hashing, header inspection, sandboxing). The `magic` output is only metadata confirming the file type, so it’s documented in notes but not stored as evidence

then i go to [any.run](http://any.run)  let it analyze and i go one by one processes and found the flag

<img width="1287" height="694" alt="image" src="https://github.com/user-attachments/assets/76ce9059-53d1-43c9-8f2d-1d692013c70a" />

at frirst i thought thats the flag, but i need to change to md5 first and submit it

<img width="336" height="531" alt="image" src="https://github.com/user-attachments/assets/77ab9132-3c97-415b-8573-5b531233bbd7" />
