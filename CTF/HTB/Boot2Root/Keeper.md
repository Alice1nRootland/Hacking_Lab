<img width="700" height="638" alt="image" src="https://github.com/user-attachments/assets/5c5b3cec-1a08-42f4-a4b1-bb17f69ec2ef" />

> How many open TCP ports are listening on Keeper?
> 

<img width="898" height="234" alt="image" src="https://github.com/user-attachments/assets/dcb214b6-748f-412a-9af6-92d6f285cc66" />

AS usual i will start scanning and the answer is 2

> What is the default password for the default user on Request Tracker (RT)?
> 

will do some research on this 

<img width="699" height="409" alt="image" src="https://github.com/user-attachments/assets/b41dd2b6-e541-4f6e-a3bb-5a7960fa55f7" />

the answer is password

> Besides root, what other user is in RT?
> 

after i login to the site 

http://tickets.keeper.htb/

<img width="1524" height="566" alt="image" src="https://github.com/user-attachments/assets/f0179bec-1f4f-461e-9c70-46a45850617e" />

I navigate to user section, there you can find another username 

the answer is `Inorgaard`

> What is the lnorgaard user's password on Keeper?
> 

then i clicked the username and bring to Inorgaard page 

<img width="883" height="716" alt="image" src="https://github.com/user-attachments/assets/000dd7de-7a8b-4fdd-8dd1-21e45ed7505d" />

there you can find the password of this username `Welcome2023!`

> Submit the flag located in the lnorgaard user's home directory.
> 

i use the cred to login through SSH 

<img width="895" height="513" alt="image" src="https://github.com/user-attachments/assets/bb87879c-6830-4114-8bbf-d77a17fbfdfc" />

and found the user flag!

> What is the 2023 CVE ID for a vulnerability in KeePass that allows an attacker access to the database's master password from a memory dump?
> 

as usual did some googling 

<img width="1575" height="455" alt="image" src="https://github.com/user-attachments/assets/0acd7da0-ff50-448e-a772-5c639c23d9b4" />

the answer 

CVE-2023-32784

> What is the master password for passcodes.kdbx?
> 

here comes the hard part 

<img width="904" height="102" alt="image" src="https://github.com/user-attachments/assets/414bac3e-284e-4264-8c1b-04478019186c" />

i found the zip file here i tried to download it 

<img width="921" height="251" alt="image" src="https://github.com/user-attachments/assets/7c4c91bc-5c75-4cad-a19b-fe586100f5fc" />

and check the file found the keepass dump

and because we are dealing with CVE-2023-32784 i use this tool
`$ git clone https://github.com/CMEPW/keepass-dump-masterkey`

<img width="911" height="267" alt="image" src="https://github.com/user-attachments/assets/39c26d7c-078c-4ff2-b9b2-e003f70d7902" />

run the python command, at first its kind weird then ii did some digging about this string

<img width="863" height="380" alt="image" src="https://github.com/user-attachments/assets/2b166dee-e9fa-4eb9-a34b-4b6ac776793c" />

and found the password and the asnwer

`rødgrød med fløde`

> What is the first line of the "Notes" section for the entry in the database containing a private SSH key?
> 

i used the password to unlock the KeePass 

<img width="805" height="633" alt="image" src="https://github.com/user-attachments/assets/ef5c2059-7737-4ebf-97f1-153c33bb3e8a" />

tHEN ON NETWORK SECTION>KEEPER.HTB I FOUND THE ANSWER

<img width="808" height="635" alt="image" src="https://github.com/user-attachments/assets/0fa50d6b-5c50-44b5-9356-bdcced8a8aed" />

which is `PuTTY-User-Key-File-3: ssh-rsa`

> Submit the flag located in the root user's home directory.
> 

then I save the content in notes as keeper.txt

copy the all content as save as keeper.txt

<img width="910" height="216" alt="image" src="https://github.com/user-attachments/assets/6b6047c9-04a2-44db-9c38-cd2ae9e0ea60" />

<img width="897" height="297" alt="image" src="https://github.com/user-attachments/assets/7bb6880f-2005-459f-b813-1bc8e5a6572b" />

then i ran as SSH and found the flag!
