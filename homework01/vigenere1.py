def encrypt_vigenere(plaintext: str, key: str) -> str:
    alfavit = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    small_alfavit = alfavit.lower()
    shifr_text = ''
    for i in range(len(plaintext)):
        if plaintext[i] in alfavit:
            shift = ord(key[i % len(key)]) - ord('A')
            shifr_text += alfavit[(alfavit.index(plaintext[i]) + shift) % len(alfavit)]
        elif plaintext[i] in small_alfavit:
            shift = ord(key[i % len(key)]) - ord('a')
            shifr_text += small_alfavit[(small_alfavit.index(plaintext[i]) + shift) % len(small_alfavit)]
        else:
            shifr_text += plaintext[i]
    return shifr_text


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    alfavit = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    small_alfavit = alfavit.lower()
    plaintext = ''
    for i in range(len(ciphertext)):
        if ciphertext[i] in alfavit:
            shift = ord(keyword[i % len(keyword)]) - ord('A')
            plaintext += alfavit[(alfavit.index(ciphertext[i]) - shift) % len(alfavit)]
        elif ciphertext[i] in small_alfavit:
            shift = ord(keyword[i % len(keyword)]) - ord('a')
            plaintext += small_alfavit[(small_alfavit.index(ciphertext[i]) - shift) % len(small_alfavit)]
        else:
            plaintext += ciphertext[i]
    return plaintext
