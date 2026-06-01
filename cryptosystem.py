import hashlib

def seed_to_initial_state(seed, width):
    seed_bytes = seed.to_bytes((seed.bit_length() + 7) // 8 or 1, 'big')
    digest = hashlib.sha256(seed_bytes).digest()
    bits = []
    for byte in digest:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
            if len(bits) == width:
                return bits
    return bits[:width]

def pattern_generator(rule_number, generations, seed):
    rule_bin = f"{rule_number:08b}"
    width = 2 * generations + 1
    
    # Replace direct seed unpacking with hashed initial state
    current = seed_to_initial_state(seed, width)
    
    all_lines = [current[:]]
    for _ in range(generations):
        padded = [0] + current + [0]
        new_row = []
        for i in range(len(padded) - 2):
            left, center, right = padded[i], padded[i+1], padded[i+2]
            neighborhood = (left << 2) | (center << 1) | right
            new_row.append(int(rule_bin[7 - neighborhood]))
        current = new_row
        all_lines.append(current[:])
    return all_lines


def generate_keystream(rule, seed, length_needed):
    grid = pattern_generator(rule, length_needed, seed)
    center = len(grid[0]) // 2
    bits = [row[center] for row in grid[1:]]
    return bits[:length_needed]


def encrypt(message, rule, seed):
    message_bytes = message.encode()
    bits_needed = len(message_bytes) * 8
    keystream = generate_keystream(rule, seed, bits_needed)
    return xor_bytes(message_bytes, keystream)

def xor_bytes(message, keystream_bits):
    result = []
    for i, byte in enumerate(message):
        keystream_byte = 0
        for bit in range(8):
            keystream_byte = (keystream_byte << 1) | keystream_bits[i * 8 + bit]
        result.append(byte ^ keystream_byte)
    return bytes(result)

def decrypt(ciphertext, rule, seed):
    bits_needed = len(ciphertext) * 8
    keystream = generate_keystream(rule, seed, bits_needed)
    try:
        return xor_bytes(ciphertext, keystream).decode('utf-8')
    except UnicodeDecodeError:
        return None


while True:
    choice = input("Do you want to encrypt or decrypt a message?")
    if choice.lower() == "encrypt":
        try:
            seed = int(input("What seed do you want to encrypt this message with?"))
        except ValueError:
            print("Please enter an integer: ")
        message = input("Enter your message: ")
        ciphertext = encrypt(message, 30, seed)
        text = decrypt(ciphertext, 30, seed)
        print("Cipher text: ", ciphertext.hex())
    if choice.lower() == "decrypt":
        try:
            seed = int(input("What seed decrypts this message? "))
        except ValueError:
            print("Please enter an integer")
            continue
        hex_input = input("Put your ciphertext in here: ")
        try:
            ciphertext = bytes.fromhex(hex_input)
        except ValueError:
            print("Invalid hex input")
            continue
        
        result = decrypt(ciphertext, 30, seed)
        if result is None:
            print("Decryption failed — wrong seed or corrupted ciphertext")
        else:
            print("Decrypted text:", result)
            
