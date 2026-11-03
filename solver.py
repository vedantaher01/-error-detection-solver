import re


# ======================================================================
# Helpers
# ======================================================================
def _bit_strings(text, min_len=4):
    """Standalone binary strings (only 0/1) of at least min_len digits.
    Ignores things like 'Problem 1' or '8-bit'."""
    pattern = r"(?<![0-9A-Za-z])[01]{%d,}(?![0-9A-Za-z])" % min_len
    return re.findall(pattern, text)


def _parity_type(lower_text):
    m = re.search(r"\b(even|odd)\b[\s-]*parity", lower_text)
    if m:
        return m.group(1)
    m = re.search(r"parity[^.]{0,30}?\b(even|odd)\b", lower_text)
    if m:
        return m.group(1)
    return "even"


def _even_odd(n):
    return "even" if n % 2 == 0 else "odd"


def _is_pow2(x):
    return (x & (x - 1)) == 0


def _md(*blocks):
    """Join markdown blocks with blank lines (skips empty ones)."""
    return "\n\n".join(b for b in blocks if b)


def _code(text):
    return "```\n" + text + "\n```"


def _table(rows):
    header = "| " + " | ".join(rows[0]) + " |"
    divider = "|" + "---|" * len(rows[0])
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join([header, divider] + body)


def _spaced(bits):
    return " ".join(bits)


def _plus_sum(bits):
    return " + ".join(bits)


def _tips(*items):
    return "### Exam tips\n" + "\n".join("- " + i for i in items)


# ======================================================================
# Method detection
# ======================================================================
def detect_method(problem_text):
    lower = problem_text.lower()

    # Hamming is checked first because its problems also mention "parity".
    if "hamming" in lower:
        return "hamming"
    if re.search(r"\bcrc\b", lower) or "cyclic redundancy" in lower or "generator polynomial" in lower:
        return "crc"
    if "checksum" in lower or "check sum" in lower:
        return "checksum"
    if "parity" in lower:
        return "parity"
    return "unknown"


# ======================================================================
# PARITY
# ======================================================================
_PARITY_CONCEPT = _md(
    "### Concept",
    "A **parity bit** is one extra bit added to the data so that the total number of 1s "
    "follows a fixed rule. With **even parity** the total number of 1s must be even; "
    "with **odd parity** it must be odd. The receiver recounts the 1s: if the rule is "
    "broken, an error is detected.",
)


def solve_parity(problem_text):
    lower = problem_text.lower()
    bits = _bit_strings(problem_text)
    if not bits:
        return {
            "method": "parity",
            "status": "error",
            "message": "No binary data (at least 4 bits) found in the problem statement."
        }

    parity = _parity_type(lower)
    rule = "EVEN" if parity == "even" else "ODD"

    # Only a received word is given -> just run the receiver check
    check_only = bool(
        len(bits) == 1
        and re.search(r"receiv|arriv", lower)
        and not re.search(r"transmit|sender|\bsend|find the parity|compute|calculate|generate", lower)
    )

    if check_only:
        received = bits[0]
        r_ones = received.count("1")
        passes = (r_ones % 2 == 0) if parity == "even" else (r_ones % 2 == 1)
        verdict = (
            "It matches, so the check **passes** and **no error is detected**."
            if passes else
            "It does not match, so the check **fails** and an **error is detected**."
        )
        explanation = _md(
            _PARITY_CONCEPT,
            "### Given",
            f"- Received word: `{received}`\n- Scheme: **{parity} parity** (the number of 1s must be {rule})",
            "### Step 1: Count the 1s in the received word",
            _code(f"{_plus_sum(received)} = {r_ones}"),
            f"The count is **{r_ones}**, which is **{_even_odd(r_ones)}**.",
            "### Step 2: Compare with the rule",
            f"The rule needs an **{parity}** number of 1s. {verdict}",
            _tips(
                "Always write the count of 1s explicitly. Examiners give marks for it.",
                "Parity only detects an **odd** number of bit errors (1, 3, 5, ...). "
                "If 2 bits flip, the count stays the same and the error is missed.",
                "Parity can tell you THAT something is wrong, never WHICH bit is wrong.",
            ),
            "### Final answer",
            f"- Number of 1s in `{received}`: **{r_ones}** ({_even_odd(r_ones)})\n"
            f"- Error detected: **{'No' if passes else 'Yes'}**",
        )
        return {
            "method": "parity",
            "status": "success",
            "received": received,
            "parity": parity,
            "received_ones": str(r_ones),
            "error_detected": "No" if passes else "Yes",
            "explanation": explanation,
        }

    data = bits[0]
    received = bits[1] if len(bits) > 1 else None
    ones = data.count("1")
    already_ok = (ones % 2 == 0) == (parity == "even")
    parity_bit = "0" if already_ok else "1"
    codeword = data + parity_bit
    total = ones + int(parity_bit)

    reason = (
        "The count already follows the rule, so we add **0** (it must not change the count)."
        if already_ok else
        "The count breaks the rule, so we add **1** to fix it."
    )

    blocks = [
        _PARITY_CONCEPT,
        "### Given",
        f"- Data bits: `{data}`\n- Scheme: **{parity} parity** (the total number of 1s must be {rule})",
        "### Step 1: Count the 1s in the data",
        _table([["Position"] + [str(i + 1) for i in range(len(data))], ["Bit"] + list(data)]),
        _code(f"{_plus_sum(data)} = {ones}"),
        f"The data has **{ones}** ones, which is **{_even_odd(ones)}**.",
        "### Step 2: Decide the parity bit",
        _table([
            ["Number of 1s in data", "Even parity bit", "Odd parity bit"],
            ["Even", "0", "1"],
            ["Odd", "1", "0"],
        ]),
        f"We need **{parity}** parity and the count is **{_even_odd(ones)}**. {reason} "
        f"So the parity bit is **{parity_bit}**.",
        "### Step 3: Build the transmitted codeword",
        f"Codeword = data + parity bit = `{data}` + `{parity_bit}` = **`{codeword}`**",
        f"Check: total 1s = {ones} + {parity_bit} = {total}, which is {_even_odd(total)} "
        f"{'✓' if (total % 2 == 0) == (parity == 'even') else '✗'}",
    ]

    result = {
        "method": "parity",
        "status": "success",
        "data": data,
        "parity": parity,
        "parity_bit": parity_bit,
        "final_code": codeword,
    }

    final_lines = [
        f"- Parity bit: **{parity_bit}**",
        f"- Transmitted codeword: **`{codeword}`**",
    ]

    if received:
        r_ones = received.count("1")
        passes = (r_ones % 2 == 0) if parity == "even" else (r_ones % 2 == 1)

        blocks += [
            "### Step 4: Receiver check",
            f"The receiver gets `{received}` and counts its 1s:",
            _code(f"{_plus_sum(received)} = {r_ones}"),
            f"The count is **{r_ones}** ({_even_odd(r_ones)}). The rule needs {rule}. "
            + ("The check **passes**, so the receiver says **no error detected**."
               if passes else
               "The check **fails**, so the receiver says **error detected**."),
        ]

        flipped = []
        if len(received) == len(codeword):
            flipped = [i + 1 for i, (a, b) in enumerate(zip(codeword, received)) if a != b]
            marks = " ".join("^" if a != b else " " for a, b in zip(codeword, received))
            blocks += [
                "### Step 5: Compare with what was really sent",
                _code(
                    f"Sent     : {_spaced(codeword)}\n"
                    f"Received : {_spaced(received)}\n"
                    f"Changed  : {marks}"
                ),
            ]
            pos_text = ", ".join(map(str, flipped))
            if flipped and passes:
                blocks.append(
                    f"**{len(flipped)} bits changed** (positions {pos_text}) but the receiver still says "
                    f"'no error'. Flipping an even number of bits keeps the count of 1s even, so a single "
                    f"parity bit **cannot detect it**. This is the main weakness of parity checking "
                    f"(CRC and Hamming codes are stronger)."
                )
            elif flipped:
                blocks.append(
                    f"{len(flipped)} bit(s) changed (position(s) {pos_text}). Parity detected it, "
                    f"but it cannot say which bit is wrong, so it cannot correct it."
                )
            else:
                blocks.append("The received word is identical to the transmitted codeword, so nothing was corrupted.")

        result["received"] = received
        result["received_ones"] = str(r_ones)
        result["error_detected"] = "No" if passes else "Yes"
        if flipped:
            result["bits_actually_flipped"] = ", ".join(map(str, flipped))

        final_lines.append(
            f"- Received word `{received}`: **{r_ones}** ones, error detected: **{'No' if passes else 'Yes'}**"
        )

    blocks += [
        _tips(
            "State the parity type (even/odd) before you start.",
            "Show the count of 1s as a sum. Examiners give marks for working.",
            "After adding the parity bit, recount the 1s in the full codeword as a check.",
            "Parity detects only an **odd** number of bit errors and can never correct them.",
            "Follow the question if it asks for the parity bit at the start instead of the end.",
        ),
        "### Final answer",
        "\n".join(final_lines),
    ]

    result["explanation"] = _md(*blocks)
    return result


# ======================================================================
# CHECKSUM (1's complement addition)
# ======================================================================
def _ones_add(a, b, width):
    mask = (1 << width) - 1
    total = a + b
    while total >> width:
        total = (total & mask) + (total >> width)
    return total


def solve_checksum(problem_text):
    lower = problem_text.lower()
    words = _bit_strings(problem_text)
    if not words:
        return {
            "method": "checksum",
            "status": "error",
            "message": "No binary data words found. Write the words in binary, e.g. 10110011."
        }

    width = max(len(w) for w in words)
    m = re.search(r"(\d+)\s*-?\s*bit", lower)
    if m and int(m.group(1)) >= width:
        width = int(m.group(1))
    mask = (1 << width) - 1

    def fmt(x):
        return format(x, "0%db" % width)

    pad = [w.zfill(width) for w in words]
    running = int(pad[0], 2)

    step_blocks = []
    for k, w in enumerate(pad[1:], start=1):
        value = int(w, 2)
        raw = running + value
        new = _ones_add(running, value, width)
        work = "\n".join([
            "  " + fmt(running),
            "+ " + fmt(value),
            "-" * (width + 2),
            " " + format(raw, "0%db" % (width + 1)),
        ])
        if raw > mask:
            low = raw & mask
            note = (
                f"The result has {width + 1} bits, so there is a **carry out of 1**. "
                f"Wrap it around by adding the carry back to the rightmost bit: "
                f"`{fmt(low)}` + `{fmt(1)}` = `{fmt(new)}`."
            )
        else:
            note = "There is no carry out of the leftmost bit, so nothing to wrap around."
        step_blocks.append(_md(
            f"**Addition {k}:** running sum + word {k + 1}",
            _code(work),
            note,
            f"Running sum = `{fmt(new)}`",
        ))
        running = new

    checksum = mask ^ running
    verify = _ones_add(running, checksum, width)
    transmitted = " ".join(pad + [fmt(checksum)])
    ok = verify == mask

    word_list = "\n".join(f"- Word {i + 1}: `{w}`" for i, w in enumerate(pad))

    explanation = _md(
        "### Concept",
        "The **checksum** is a check value built from the data. The sender adds all the data words "
        "using **1's complement addition** (any carry out of the leftmost bit is wrapped around and "
        "added back), then flips every bit of the sum. The receiver adds everything, including the "
        "checksum. If nothing went wrong, the total is **all 1s**.",
        "### Given",
        f"There are **{len(pad)} words** of **{width} bits**:\n{word_list}",
        "### Step 1: Add the words with wrap-around carry",
        "Add the words one at a time. If the addition produces a carry out of the leftmost bit, "
        "add that carry back at the right end.",
        _md(*step_blocks) if step_blocks else "There is only one word, so the sum is the word itself.",
        f"**Final sum of the data words = `{fmt(running)}`**",
        "### Step 2: Take the 1's complement",
        "Flip every bit of the sum (0 becomes 1, 1 becomes 0):",
        _code(f"Sum      : {fmt(running)}\nChecksum : {fmt(checksum)}"),
        "### Step 3: Transmitted data",
        "The sender sends the data words followed by the checksum:",
        _code(transmitted),
        "### Step 4: Receiver check",
        f"The receiver adds all data words and the checksum: `{fmt(running)}` + `{fmt(checksum)}` = `{fmt(verify)}`.",
        ("This is **all 1s**, so the receiver concludes there is **no error**."
         if ok else
         "This is **not all 1s**, so the receiver concludes an **error was detected**."),
        _tips(
            "Always write every word with the same number of bits (pad with leading zeros).",
            "Never forget the wrap-around carry. It is the most common mistake.",
            "Checksum = the 1's complement (flip all bits) of the sum, not the sum itself.",
            "At the receiver, 'all 1s' means no error. Complementing that total gives all 0s.",
            "Some textbooks add in hexadecimal or decimal. The same wrap-around idea applies.",
        ),
        "### Final answer",
        f"- Sum: **`{fmt(running)}`**\n"
        f"- Checksum: **`{fmt(checksum)}`**\n"
        f"- Transmitted: **`{transmitted}`**\n"
        f"- Receiver check: **{'No error' if ok else 'Error detected'}**",
    )

    return {
        "method": "checksum",
        "status": "success",
        "words": ", ".join(pad),
        "sum": fmt(running),
        "checksum": fmt(checksum),
        "transmitted": transmitted,
        "receiver_check": "No error" if ok else "Error detected",
        "explanation": explanation,
    }


# ======================================================================
# CRC
# ======================================================================
_POLY_RE = re.compile(
    r"\bx\^?\d*(?![A-Za-z])(?:\s*\+\s*(?:x\^?\d*|1)(?![0-9A-Za-z]))*"
)


def _poly_to_bits(expr):
    exps = []
    for term in expr.replace(" ", "").split("+"):
        if term == "1":
            exps.append(0)
        else:
            m = re.fullmatch(r"x\^?(\d*)", term)
            if not m:
                return None
            exps.append(int(m.group(1)) if m.group(1) else 1)
    degree = max(exps)
    return "".join("1" if (degree - i) in exps else "0" for i in range(degree + 1))


def _mod2_division(bits, generator):
    """Modulo-2 (XOR) long division.
    Returns (remainder, steps) where each step is (bit_position, window_before, window_after)."""
    arr = [int(b) for b in bits]
    gen = [int(b) for b in generator]
    g = len(gen)
    steps = []
    for i in range(len(arr) - g + 1):
        if arr[i]:
            window = "".join(str(b) for b in arr[i:i + g])
            for j in range(g):
                arr[i + j] ^= gen[j]
            after = "".join(str(b) for b in arr[i:i + g])
            steps.append((i + 1, window, after))
    remainder = "".join(str(b) for b in arr[-(g - 1):])
    return remainder, steps


def crc_remainder(data_bits, generator_bits):
    appended = data_bits + "0" * (len(generator_bits) - 1)
    remainder, _ = _mod2_division(appended, generator_bits)
    return remainder


def _division_steps_text(steps, g, gen):
    if not steps:
        return "There is no leading 1 to divide, so no XOR step is needed."
    lines = []
    for k, (pos, window, after) in enumerate(steps, start=1):
        lines.append(
            f"{k}. Leading 1 is at bit {pos}. Take the next {g} bits `{window}` "
            f"and XOR with `{gen}` gives `{after}`."
        )
    return "\n".join(lines)


def solve_crc(problem_text):
    lower = problem_text.lower()

    generator = None
    poly_expr = None
    poly_match = _POLY_RE.search(lower)
    if poly_match:
        generator = _poly_to_bits(poly_match.group(0))
        if generator:
            poly_expr = poly_match.group(0).strip()
    if generator is None:
        g_m = re.search(r"(?:divisor|generator|polynomial)[^01]*([01]{3,})", lower)
        if g_m:
            generator = g_m.group(1)

    if not generator or len(generator) < 2 or generator[0] != "1":
        return {
            "method": "crc",
            "status": "error",
            "message": "Could not find the generator polynomial (e.g. 'x^4 + x + 1' or 'divisor 10011')."
        }

    strings = [b for b in _bit_strings(problem_text) if b != generator]

    d_m = re.search(r"data[^01]*([01]{4,})", lower)
    data = d_m.group(1) if d_m else (strings[0] if strings else None)
    if not data:
        return {
            "method": "crc",
            "status": "error",
            "message": "Could not find the data bits in the problem statement."
        }

    r_m = re.search(r"receiv\w*[^01]*([01]{4,})", lower)
    received = r_m.group(1) if r_m else next((s for s in strings if s != data), None)

    g = len(generator)
    degree = g - 1
    zeros = "0" * degree
    appended = data + zeros

    remainder, steps = _mod2_division(appended, generator)
    codeword = data + remainder

    powers = [f"x^{degree - i}" for i in range(g)]
    poly_table = _table([["Power"] + powers, ["Coefficient"] + list(generator)])
    if poly_expr:
        poly_line = (
            f"The generator polynomial `{poly_expr}` becomes bits by writing **1** for every power "
            f"that is present and **0** for every power that is missing:"
        )
    else:
        poly_line = "The generator is given directly as bits. As a polynomial it reads:"

    blocks = [
        "### Concept",
        "**CRC (Cyclic Redundancy Check)** treats the data bits as a polynomial and divides it by a "
        "fixed **generator** using **modulo-2 division** (XOR, with no borrows or carries). The "
        "remainder is attached to the data. The receiver divides the whole received word by the same "
        "generator: a remainder of **0** means no error was detected.",
        "### Given",
        f"- Data bits: `{data}`\n- Generator: `{generator}`" + (f" (from `{poly_expr}`)" if poly_expr else ""),
        "### Step 1: Convert the generator to bits",
        poly_line,
        poly_table,
        f"Generator bits = **`{generator}`** (length {g}, degree {degree}).",
        "### Step 2: Append zeros to the data",
        f"Append **{degree} zeros** (the degree of the generator) to the data:",
        _code(f"{data} + {zeros} = {appended}"),
        "### Step 3: Modulo-2 division",
        "XOR rules: 0 XOR 0 = 0, 0 XOR 1 = 1, 1 XOR 0 = 1, 1 XOR 1 = 0.",
        "Method: look at the leftmost remaining 1. Take that bit and the next "
        f"{degree} bits (a window of {g} bits), XOR the window with the generator, then move on to "
        "the next leftmost 1. If the leftmost bit is 0, just move one place right (nothing to XOR).",
        _division_steps_text(steps, g, generator),
        f"After the last step, the final {degree} bits are the remainder: **`{remainder}`**.",
        "### Step 4: Build the transmitted codeword",
        f"Codeword = data + remainder = `{data}` + `{remainder}` = **`{codeword}`**",
    ]

    result = {
        "method": "crc",
        "status": "success",
        "data": data,
        "generator": generator,
        "remainder": remainder,
        "final_code": codeword,
    }

    final_lines = [
        f"- CRC remainder: **`{remainder}`**",
        f"- Transmitted codeword: **`{codeword}`**",
    ]

    if received:
        check, check_steps = _mod2_division(received, generator)
        ok = set(check) <= {"0"}
        blocks += [
            "### Step 5: Receiver check",
            f"The receiver divides the received word `{received}` by `{generator}` (no extra zeros this time):",
            _division_steps_text(check_steps, g, generator),
            f"The remainder is **`{check}`**. "
            + ("It is all zeros, so **no error is detected**."
               if ok else
               "It is not zero, so an **error is detected**."),
        ]
        result["received"] = received
        result["received_remainder"] = check
        result["error_detected"] = "No" if ok else "Yes"
        final_lines.append(
            f"- Received `{received}`: remainder `{check}`, error detected: **{'No' if ok else 'Yes'}**"
        )

    blocks += [
        _tips(
            f"The remainder always has exactly {degree} bits. Pad it with leading zeros if needed (e.g. 11 becomes 011).",
            "Only XOR when the leftmost bit of the window is 1. If it is 0, shift one place.",
            "At the receiver, do NOT append zeros. Divide the full received word.",
            "Receiver remainder 0 = no error detected. Non-zero = error detected.",
            "To get the generator from a polynomial, write 1 for each power present, "
            "including the invisible 1 in front of the x terms and the constant term.",
        ),
        "### Final answer",
        "\n".join(final_lines),
    ]

    result["explanation"] = _md(*blocks)
    return result


# ======================================================================
# HAMMING CODE
# ======================================================================
def _roles(n):
    roles = [""]
    d = 0
    for pos in range(1, n + 1):
        if _is_pow2(pos):
            roles.append(f"p{pos}")
        else:
            d += 1
            roles.append(f"d{d}")
    return roles


def _layout_table(n, roles, bit_labels):
    r = n.bit_length()
    return _table([
        ["Position"] + [str(p) for p in range(1, n + 1)],
        ["Binary"] + [format(p, "0%db" % r) for p in range(1, n + 1)],
        ["Role"] + [roles[p] for p in range(1, n + 1)],
        ["Bit"] + bit_labels,
    ])


def _hamming_encode(data, parity):
    m = len(data)
    r = 2
    tried = []
    while True:
        ok = 2 ** r >= m + r + 1
        tried.append((r, 2 ** r, m + r + 1, ok))
        if ok:
            break
        r += 1
    n = m + r
    roles = _roles(n)

    code = [0] * (n + 1)
    j = 0
    for pos in range(1, n + 1):
        if not _is_pow2(pos):
            code[pos] = int(data[j])
            j += 1

    checks = []
    for i in range(r):
        p = 2 ** i
        covered = [pos for pos in range(1, n + 1) if (pos & p) and pos != p]
        vals = [code[pos] for pos in covered]
        ones = sum(vals)
        bit = ones % 2 if parity == "even" else (ones + 1) % 2
        code[p] = bit
        checks.append({"p": p, "covered": covered, "vals": vals, "ones": ones, "bit": bit})
    return code, roles, n, r, tried, checks


def _hamming_checks(codeword, parity):
    n = len(codeword)
    bits = [0] + [int(b) for b in codeword]
    syndrome = 0
    checks = []
    p = 1
    while p <= n:
        covered = [pos for pos in range(1, n + 1) if pos & p]
        vals = [bits[pos] for pos in covered]
        ones = sum(vals)
        bad = (ones % 2 == 1) if parity == "even" else (ones % 2 == 0)
        if bad:
            syndrome += p
        checks.append({"p": p, "covered": covered, "vals": vals, "ones": ones, "bad": bad})
        p *= 2
    return syndrome, checks


_HAMMING_CONCEPT = _md(
    "### Concept",
    "A **Hamming code** puts parity bits at the positions that are powers of 2 (1, 2, 4, 8, ...). "
    "Each parity bit checks a different group of positions: parity bit **p** checks every position "
    "whose binary form has a 1 in the place worth **p**. When a word arrives, the parity checks that "
    "fail add up to a number called the **syndrome**. The syndrome is the **position of a single "
    "wrong bit**, so Hamming codes can both detect and correct one-bit errors.",
)


def solve_hamming(problem_text):
    lower = problem_text.lower()
    parity = _parity_type(lower)
    rule = "EVEN" if parity == "even" else "ODD"
    bits = _bit_strings(problem_text)
    if not bits:
        return {
            "method": "hamming",
            "status": "error",
            "message": "No binary data found in the problem statement."
        }

    s = bits[0]
    n_s = len(s)
    is_codeword_length = ((n_s + 1) & n_s) == 0  # 7, 15, 31, ...
    wants_decode = bool(re.search(
        r"receiv|arriv|syndrome|locate|\bcorrect\b|\bcorrected\b|which bit", lower))

    # ------------------------------------------------------------------
    # ENCODING: data bits -> Hamming codeword
    # ------------------------------------------------------------------
    if not (is_codeword_length and wants_decode):
        code, roles, n, r, tried, checks = _hamming_encode(s, parity)
        codeword = "".join(str(b) for b in code[1:])

        tried_table = _table(
            [["r (parity bits)", "2^r", f"m + r + 1 (m = {len(s)})", "2^r >= m + r + 1 ?"]]
            + [[str(a), str(b), str(c), "Yes" if ok else "No"] for a, b, c, ok in tried]
        )

        blank_bits = [("?" if _is_pow2(p) else str(code[p])) for p in range(1, n + 1)]
        final_bits = [str(code[p]) for p in range(1, n + 1)]

        check_lines = []
        for c in checks:
            p = c["p"]
            pos_txt = ", ".join(map(str, c["covered"]))
            val_txt = ", ".join(map(str, c["vals"]))
            check_lines.append(
                f"- **p{p}** checks positions {pos_txt}. Their bits are {val_txt}, so there are "
                f"**{c['ones']}** ones. For {parity} parity, p{p} = **{c['bit']}**."
            )

        explanation = _md(
            _HAMMING_CONCEPT,
            "### Given",
            f"- Data bits: `{s}` (m = {len(s)} bits)\n- Scheme: **{parity} parity** "
            f"(each group of checked bits must contain an {parity} number of 1s)",
            "### Step 1: How many parity bits are needed?",
            f"We need the smallest r that satisfies 2^r >= m + r + 1:",
            tried_table,
            f"So **r = {r}** parity bits are needed and the codeword has **n = {len(s)} + {r} = {n}** bits.",
            "### Step 2: Lay out the codeword",
            "Parity bits sit at positions 1, 2, 4, 8, ... (powers of 2). The data bits fill the other "
            "positions from left to right. `?` marks a parity bit we still have to compute.",
            _layout_table(n, roles, blank_bits),
            "### Step 3: Compute each parity bit",
            "Parity bit p covers every position whose binary form has a 1 in the place worth p "
            "(see the Binary row above).",
            "\n".join(check_lines),
            "### Step 4: Write the final codeword",
            _layout_table(n, roles, final_bits),
            f"Hamming codeword = **`{codeword}`**",
            _tips(
                "Parity bits go at positions 1, 2, 4, 8, ... counted from the left, starting at 1.",
                "Write each position in binary. It tells you exactly which parity bits cover it.",
                "A parity bit does not include itself when you count the 1s to compute it.",
                "Check at the end: every group, including its parity bit, must have an "
                f"{parity} number of 1s.",
                "Some books number positions from the right. Follow the numbering in your question.",
            ),
            "### Final answer",
            f"- Parity bits needed: **{r}**\n- Hamming codeword: **`{codeword}`**",
        )

        return {
            "method": "hamming",
            "status": "success",
            "data": s,
            "parity": parity,
            "final_code": codeword,
            "explanation": explanation,
        }

    # ------------------------------------------------------------------
    # DECODING: find and correct a single-bit error
    # ------------------------------------------------------------------
    n = n_s
    roles = _roles(n)
    syndrome, checks = _hamming_checks(s, parity)
    r = len(checks)
    syndrome_bits = "".join("1" if c["bad"] else "0" for c in reversed(checks))

    check_lines = []
    for c in checks:
        p = c["p"]
        pos_txt = ", ".join(map(str, c["covered"]))
        val_txt = ", ".join(map(str, c["vals"]))
        check_lines.append(
            f"- **p{p}** checks positions {pos_txt}. Their bits are {val_txt}, so there are "
            f"**{c['ones']}** ones ({_even_odd(c['ones'])}). Needed: {rule}. "
            + ("**FAILS**, so this check contributes " + str(p) + "." if c["bad"]
               else "OK, so this check contributes 0.")
        )

    failing = [str(c["p"]) for c in checks if c["bad"]]
    if failing:
        sum_line = f"Failing checks: p{', p'.join(failing)}. Syndrome = {' + '.join(failing)} = **{syndrome}**."
    else:
        sum_line = "No check failed, so the syndrome = **0**."

    blocks = [
        _HAMMING_CONCEPT,
        "### Given",
        f"- Received codeword: `{s}` (positions 1 to {n}, left to right)\n"
        f"- Scheme: **{parity} parity** (each checked group must contain an {rule} number of 1s)",
        "### Step 1: Label the positions",
        "Positions that are powers of 2 are parity bits (p). The rest are data bits (d).",
        _layout_table(n, roles, list(s)),
        "### Step 2: Run each parity check",
        "\n".join(check_lines),
        "### Step 3: Compute the syndrome",
        sum_line,
        f"Written in binary (highest parity bit first) this is `{syndrome_bits}`.",
    ]

    result = {
        "method": "hamming",
        "status": "success",
        "received": s,
        "parity": parity,
        "syndrome": f"{syndrome_bits} ({syndrome})",
    }

    if syndrome == 0:
        corrected = s
        blocks += [
            "### Step 4: Conclusion",
            "The syndrome is **0**, so **no error is detected**. The received word is already correct.",
        ]
        result["error_position"] = "none"
    elif syndrome <= n:
        flipped_bit = "1" if s[syndrome - 1] == "0" else "0"
        corrected = s[:syndrome - 1] + flipped_bit + s[syndrome:]
        blocks += [
            "### Step 4: Locate and correct the error",
            f"The syndrome is {syndrome}, so the bit at **position {syndrome}** is wrong.",
            f"Flip it from `{s[syndrome - 1]}` to `{flipped_bit}`:",
            _code(f"Received  : {s}\nCorrected : {corrected}"),
        ]
        result["error_position"] = str(syndrome)
    else:
        blocks += [
            "### Step 4: Conclusion",
            f"The syndrome ({syndrome}) is larger than the codeword length ({n}). That means more "
            "than one bit is wrong, and a single-error-correcting Hamming code **cannot fix it**.",
            "### Final answer",
            f"- Syndrome: **{syndrome}** (invalid, so a multiple-bit error)",
        ]
        result["error_position"] = "invalid"
        result["explanation"] = _md(*blocks)
        return result

    data_bits = "".join(corrected[p - 1] for p in range(1, n + 1) if not _is_pow2(p))
    blocks += [
        "### Step 5: Extract the original data",
        f"Drop the parity bits (positions {', '.join(str(2 ** i) for i in range(r))}) from the corrected "
        f"codeword. The data bits are **`{data_bits}`**.",
        _tips(
            "Syndrome 0 means no error. A non-zero syndrome is the position of the wrong bit.",
            "Read the syndrome with the highest parity bit first (p4 p2 p1).",
            "Parity bits include themselves when you recount a group at the receiver.",
            "Hamming corrects 1 error. With 2 or more errors it may 'correct' the wrong bit.",
            "Some books number positions from the right. Follow the numbering in your question.",
        ),
        "### Final answer",
        f"- Syndrome: **{syndrome_bits}** = {syndrome}\n"
        f"- Error position: **{syndrome if syndrome else 'none'}**\n"
        f"- Corrected codeword: **`{corrected}`**\n"
        f"- Original data bits: **`{data_bits}`**",
    ]

    result["corrected_codeword"] = corrected
    result["data_bits"] = data_bits
    result["explanation"] = _md(*blocks)
    return result


# ======================================================================
# Main entry point used by app.py
# ======================================================================
def solve_problem(problem_text):
    method = detect_method(problem_text)

    try:
        if method == "parity":
            return solve_parity(problem_text)
        elif method == "checksum":
            return solve_checksum(problem_text)
        elif method == "crc":
            return solve_crc(problem_text)
        elif method == "hamming":
            return solve_hamming(problem_text)
    except Exception as e:
        return {
            "method": method,
            "status": "error",
            "message": f"Could not solve this problem: {e}"
        }

    return {
        "method": "unknown",
        "status": "error",
        "message": "The system could not detect the error detection method from the problem statement."
    }