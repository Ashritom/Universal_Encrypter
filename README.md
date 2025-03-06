# Universal_Encrypter

As we know the data is the most valuable thing on the planet, and protecting it is a complex task as hackers and unauthorised person always wants to exploit them.

For security reasons, we need to convert the original data into an unknown format to make the data unreadable , making it difficult to intercept.

This python program will cover this need and encrypt any file into an encrypted unreadable file using a key which is provided by the user (this program is focused for a single user therefore here a single key is used for both encryption and decryption {symmetric key encryption} )

Again when the same key is provided, the encrypted file gets decrypted in its original format.

if a wrong password is provided, it still shows as decryption done successfully and also create an file with the same extention as the original file but lack in content which is made with the intention to misguide the hacker.

you can differentiate the original and the encrypted file by looking at the extention, for encrypted file there is an extention .enc .
