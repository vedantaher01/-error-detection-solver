from solver import solve_problem


def test_parity():
    r = solve_problem(
        "A sender transmits the 7-bit data 1011001 using even parity. Find the parity bit "
        "and the transmitted 8-bit codeword. At the receiver, the word 10110111 arrives. "
        "Determine whether an error is detected."
    )
    assert r["parity_bit"] == "0"
    assert r["final_code"] == "10110010"
    assert r["error_detected"] == "No"


def test_checksum():
    r = solve_problem(
        "Four 8-bit data words are sent: 10110011, 01101110, 11001010 and 00111101. "
        "Compute the checksum using 1's complement addition."
    )
    assert r["sum"] == "00101010"
    assert r["checksum"] == "11010101"


def test_crc():
    r = solve_problem(
        "The data bits are 1101011011 and the generator polynomial is x^4 + x + 1 "
        "(divisor 10011). Compute the CRC remainder using modulo-2 division. "
        "Then check whether the received word 11010110111110 is error-free."
    )
    assert r["remainder"] == "1110"
    assert r["final_code"] == "11010110111110"
    assert r["error_detected"] == "No"


def test_hamming():
    r = solve_problem(
        "A Hamming (7,4) code with even parity is used. The received codeword is 1001101. "
        "Find the syndrome, locate the bit in error, and write the corrected codeword."
    )
    assert r["error_position"] == "7"
    assert r["corrected_codeword"] == "1001100"