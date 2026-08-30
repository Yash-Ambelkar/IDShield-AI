import re


# ==========================================================
# IDShield AI - Multi-Document OCR Field Extractor
# ==========================================================


# ==========================================================
# NORMALIZE TEXT
# ==========================================================

def clean_text(text):

    if text is None:
        return ""

    return str(text).strip()


def normalized_text(text):

    return re.sub(
        r"\s+",
        " ",
        clean_text(text)
    ).upper()


# ==========================================================
# FIND VALUE AFTER LABEL
# ==========================================================

def find_labeled_value(texts, labels):

    for index, text in enumerate(texts):

        current = normalized_text(text)

        for label in labels:

            label_normalized = normalized_text(label)

            # ----------------------------------------------
            # Example:
            # NAME: ARJUN SHARMA
            # ----------------------------------------------

            if current.startswith(label_normalized):

                value = current[
                    len(label_normalized):
                ].strip(" :.-")

                if value:

                    return value

                # ------------------------------------------
                # Example:
                #
                # NAME:
                # ARJUN SHARMA
                # ------------------------------------------

                if index + 1 < len(texts):

                    next_value = clean_text(
                        texts[index + 1]
                    )

                    if next_value:

                        return next_value

    return None


# ==========================================================
# FIND REGEX PATTERN
# ==========================================================

def find_pattern(texts, pattern):

    for text in texts:

        match = re.search(
            pattern,
            clean_text(text),
            re.IGNORECASE
        )

        if match:

            return match.group(0).strip()

    return None


# ==========================================================
# FIND DATE
# ==========================================================

def normalize_date(value):

    if not value:

        return None

    value = value.strip()

    value = value.replace("/", "-")
    value = value.replace(".", "-")

    return value


def find_date_after_label(texts, labels):

    for index, text in enumerate(texts):

        current = normalized_text(text)

        for label in labels:

            label_normalized = normalized_text(label)

            if current.startswith(label_normalized):

                remaining = current[
                    len(label_normalized):
                ].strip(" :.-")

                # ------------------------------------------
                # Date on same line
                # ------------------------------------------

                match = re.search(
                    r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
                    remaining
                )

                if match:

                    return normalize_date(
                        match.group(0)
                    )

                # ------------------------------------------
                # Date on next line
                # ------------------------------------------

                if index + 1 < len(texts):

                    next_text = clean_text(
                        texts[index + 1]
                    )

                    match = re.search(
                        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b",
                        next_text
                    )

                    if match:

                        return normalize_date(
                            match.group(0)
                        )

    return None


# ==========================================================
# DOCUMENT TYPE DETECTION
# ==========================================================

def detect_document_type(texts):

    full_text = " ".join(
        normalized_text(text)
        for text in texts
    )


    # ======================================================
    # PASSPORT
    # ======================================================

    passport_keywords = [

        "PASSPORT",

        "P<",

        "PLACE OF BIRTH",

        "DATE OF ISSUE"

    ]

    passport_score = sum(

        1
        for keyword in passport_keywords
        if keyword in full_text

    )


    # ======================================================
    # DRIVING LICENSE
    # ======================================================

    driving_keywords = [

        "DRIVING LICENCE",

        "DRIVING LICENSE",

        "DRIVER LICENCE",

        "DRIVER LICENSE",

        "DL NO",

        "DL NUMBER",

        "TRANSPORT"

    ]

    driving_score = sum(

        1
        for keyword in driving_keywords
        if keyword in full_text

    )


    # ======================================================
    # PAN
    # ======================================================

    pan_score = 0

    if "INCOME TAX" in full_text:

        pan_score += 2

    if "PERMANENT ACCOUNT NUMBER" in full_text:

        pan_score += 3

    if re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        full_text
    ):

        pan_score += 2


    # ======================================================
    # VOTER ID
    # ======================================================

    voter_keywords = [

        "ELECTION COMMISSION",

        "VOTER",

        "ELECTOR",

        "EPIC",

        "ELECTOR PHOTO ID"

    ]

    voter_score = sum(

        1
        for keyword in voter_keywords
        if keyword in full_text

    )


    # ======================================================
    # NATIONAL ID
    # ======================================================

    national_id_keywords = [

        "NATIONAL ID",

        "IDENTITY CARD",

        "NATIONAL IDENTITY"

    ]

    national_id_score = sum(

        1
        for keyword in national_id_keywords
        if keyword in full_text

    )


    # ======================================================
    # GENERIC IDENTITY DOCUMENT
    # ======================================================

    identity_keywords = [

        "IDENTITY DOCUMENT",

        "IDENTIFICATION DOCUMENT",

        "IDENTITY CARD",

        "IDENTIFICATION CARD"

    ]

    identity_score = sum(

        1
        for keyword in identity_keywords
        if keyword in full_text

    )


    # ======================================================
    # IMPORTANT:
    # Generic identity document should be detected
    # ======================================================

    scores = {

        "PASSPORT":
            passport_score,

        "DRIVING LICENSE":
            driving_score,

        "PAN":
            pan_score,

        "VOTER ID":
            voter_score,

        "NATIONAL ID":
            national_id_score,

        "IDENTITY DOCUMENT":
            identity_score

    }


    document_type = max(
        scores,
        key=scores.get
    )

    highest_score = scores[
        document_type
    ]


    # ------------------------------------------------------
    # No document type detected
    # ------------------------------------------------------

    if highest_score < 1:

        return {

            "document_type":
                "UNKNOWN",

            "confidence":
                0,

            "scores":
                scores

        }


    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    confidence = min(
        100,
        highest_score * 25
    )


    return {

        "document_type":
            document_type,

        "confidence":
            confidence,

        "scores":
            scores

    }


# ==========================================================
# PASSPORT EXTRACTION
# ==========================================================

def extract_passport(texts, data):

    data["document_type"] = "PASSPORT"


    data["document_number"] = find_labeled_value(
        texts,
        [
            "PASSPORT NO",
            "PASSPORT NUMBER",
            "DOCUMENT NO",
            "DOCUMENT NUMBER"
        ]
    )


    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "FULL NAME",
            "SURNAME"
        ]
    )


    data["nationality"] = find_labeled_value(
        texts,
        [
            "NATIONALITY"
        ]
    )


    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB",
            "BIRTH DATE"
        ]
    )


    data["date_of_expiry"] = find_date_after_label(
        texts,
        [
            "DATE OF EXPIRY",
            "EXPIRY DATE",
            "EXPIRATION DATE"
        ]
    )


    data["gender"] = find_labeled_value(
        texts,
        [
            "GENDER",
            "SEX"
        ]
    )


    return data


# ==========================================================
# DRIVING LICENSE EXTRACTION
# ==========================================================

def extract_driving_license(texts, data):

    data["document_type"] = "DRIVING LICENSE"


    data["document_number"] = find_labeled_value(
        texts,
        [
            "DL NO",
            "DL NUMBER",
            "LICENCE NO",
            "LICENSE NO",
            "LICENCE NUMBER",
            "LICENSE NUMBER"
        ]
    )


    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "FULL NAME"
        ]
    )


    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB"
        ]
    )


    data["date_of_expiry"] = find_date_after_label(
        texts,
        [
            "VALID TILL",
            "VALID UPTO",
            "EXPIRY DATE",
            "DATE OF EXPIRY"
        ]
    )


    data["gender"] = find_labeled_value(
        texts,
        [
            "GENDER",
            "SEX"
        ]
    )


    data["nationality"] = find_labeled_value(
        texts,
        [
            "NATIONALITY"
        ]
    )


    return data


# ==========================================================
# PAN EXTRACTION
# ==========================================================

def extract_pan(texts, data):

    data["document_type"] = "PAN"


    data["document_number"] = find_pattern(
        texts,
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    )


    if not data["document_number"]:

        data["document_number"] = find_labeled_value(
            texts,
            [
                "PAN NO",
                "PAN NUMBER",
                "PERMANENT ACCOUNT NUMBER"
            ]
        )


    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "FULL NAME"
        ]
    )


    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB"
        ]
    )


    data["nationality"] = "INDIAN"

    data["date_of_expiry"] = None

    data["gender"] = None


    return data


# ==========================================================
# VOTER ID EXTRACTION
# ==========================================================

def extract_voter_id(texts, data):

    data["document_type"] = "VOTER ID"


    data["document_number"] = find_labeled_value(
        texts,
        [
            "EPIC NO",
            "EPIC NUMBER",
            "VOTER ID",
            "VOTER ID NO"
        ]
    )


    if not data["document_number"]:

        data["document_number"] = find_pattern(
            texts,
            r"\b[A-Z]{3}[0-9]{7}\b"
        )


    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "ELECTOR NAME",
            "FULL NAME"
        ]
    )


    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB"
        ]
    )


    data["gender"] = find_labeled_value(
        texts,
        [
            "GENDER",
            "SEX"
        ]
    )


    data["nationality"] = "INDIAN"

    data["date_of_expiry"] = None


    return data


# ==========================================================
# NATIONAL ID EXTRACTION
# ==========================================================

def extract_national_id(texts, data):

    data["document_type"] = "NATIONAL ID"


    data["document_number"] = find_labeled_value(
        texts,
        [
            "ID NO",
            "ID NUMBER",
            "IDENTITY NUMBER",
            "NATIONAL ID"
        ]
    )


    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "FULL NAME"
        ]
    )


    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB"
        ]
    )


    data["gender"] = find_labeled_value(
        texts,
        [
            "GENDER",
            "SEX"
        ]
    )


    data["nationality"] = (
        find_labeled_value(
            texts,
            [
                "NATIONALITY"
            ]
        )
        or "INDIAN"
    )


    data["date_of_expiry"] = find_date_after_label(
        texts,
        [
            "EXPIRY",
            "EXPIRY DATE"
        ]
    )


    return data


# ==========================================================
# GENERIC IDENTITY DOCUMENT EXTRACTION
# ==========================================================

def extract_identity_document(texts, data):

    data["document_type"] = "IDENTITY DOCUMENT"


    # ------------------------------------------------------
    # NAME
    # ------------------------------------------------------

    data["name"] = find_labeled_value(
        texts,
        [
            "NAME",
            "FULL NAME"
        ]
    )


    # ------------------------------------------------------
    # DOCUMENT NUMBER
    # ------------------------------------------------------

    data["document_number"] = find_labeled_value(
        texts,
        [
            "DOCUMENT NUMBER",
            "DOCUMENT NO",
            "ID NUMBER",
            "ID NO",
            "IDENTITY NUMBER"
        ]
    )


    # ------------------------------------------------------
    # NATIONALITY
    # ------------------------------------------------------

    data["nationality"] = find_labeled_value(
        texts,
        [
            "NATIONALITY"
        ]
    )


    # ------------------------------------------------------
    # DATE OF BIRTH
    # ------------------------------------------------------

    data["date_of_birth"] = find_date_after_label(
        texts,
        [
            "DATE OF BIRTH",
            "DOB",
            "BIRTH DATE"
        ]
    )


    # ------------------------------------------------------
    # DATE OF EXPIRY
    # ------------------------------------------------------

    data["date_of_expiry"] = find_date_after_label(
        texts,
        [
            "DATE OF EXPIRY",
            "EXPIRY DATE",
            "EXPIRATION DATE",
            "VALID UNTIL"
        ]
    )


    # ------------------------------------------------------
    # GENDER
    # ------------------------------------------------------

    data["gender"] = find_labeled_value(
        texts,
        [
            "GENDER",
            "SEX"
        ]
    )


    # ------------------------------------------------------
    # NORMALIZE GENDER
    # ------------------------------------------------------

    if data["gender"]:

        gender = normalized_text(
            data["gender"]
        )

        if gender in [
            "M",
            "MALE"
        ]:

            data["gender"] = "M"

        elif gender in [
            "F",
            "FEMALE"
        ]:

            data["gender"] = "F"


    return data


# ==========================================================
# MAIN FIELD EXTRACTION
# ==========================================================

def extract_fields(texts):

    # ------------------------------------------------------
    # Safety
    # ------------------------------------------------------

    if not texts:

        return {

            "document_type":
                "UNKNOWN",

            "document_confidence":
                0,

            "document_number":
                None,

            "name":
                None,

            "nationality":
                None,

            "date_of_birth":
                None,

            "date_of_expiry":
                None,

            "gender":
                None,

            "raw_text":
                []

        }


    # ------------------------------------------------------
    # Clean OCR text
    # ------------------------------------------------------

    cleaned_texts = []

    for text in texts:

        value = clean_text(text)

        if value:

            cleaned_texts.append(
                value
            )


    # ------------------------------------------------------
    # Display OCR lines
    # ------------------------------------------------------

    print("\n")
    print("=" * 60)
    print("OCR TEXT RECEIVED BY FIELD EXTRACTOR")
    print("=" * 60)

    for index, text in enumerate(
        cleaned_texts
    ):

        print(
            f"{index + 1:02d}. {text}"
        )

    print("=" * 60)


    # ------------------------------------------------------
    # Detect document
    # ------------------------------------------------------

    detection = detect_document_type(
        cleaned_texts
    )

    document_type = detection[
        "document_type"
    ]


    print(
        "\nDetected document type:",
        document_type
    )

    print(
        "Detection confidence:",
        detection["confidence"],
        "%"
    )


    # ------------------------------------------------------
    # Base data
    # ------------------------------------------------------

    data = {

        "document_type":
            document_type,

        "document_confidence":
            detection["confidence"],

        "document_number":
            None,

        "name":
            None,

        "nationality":
            None,

        "date_of_birth":
            None,

        "date_of_expiry":
            None,

        "gender":
            None

    }


    # ======================================================
    # DOCUMENT-SPECIFIC EXTRACTION
    # ======================================================

    if document_type == "PASSPORT":

        data = extract_passport(
            cleaned_texts,
            data
        )


    elif document_type == "DRIVING LICENSE":

        data = extract_driving_license(
            cleaned_texts,
            data
        )


    elif document_type == "PAN":

        data = extract_pan(
            cleaned_texts,
            data
        )


    elif document_type == "VOTER ID":

        data = extract_voter_id(
            cleaned_texts,
            data
        )


    elif document_type == "NATIONAL ID":

        data = extract_national_id(
            cleaned_texts,
            data
        )


    elif document_type == "IDENTITY DOCUMENT":

        data = extract_identity_document(
            cleaned_texts,
            data
        )


    # ======================================================
    # FALLBACK EXTRACTION
    #
    # This is important if OCR does not classify the
    # document correctly.
    # ======================================================

    # ------------------------------------------------------
    # Name
    # ------------------------------------------------------

    if not data["name"]:

        data["name"] = find_labeled_value(
            cleaned_texts,
            [
                "NAME",
                "FULL NAME"
            ]
        )


    # ------------------------------------------------------
    # Document number
    # ------------------------------------------------------

    if not data["document_number"]:

        data["document_number"] = find_labeled_value(
            cleaned_texts,
            [
                "DOCUMENT NUMBER",
                "DOCUMENT NO",
                "ID NUMBER",
                "ID NO"
            ]
        )


    # ------------------------------------------------------
    # Nationality
    # ------------------------------------------------------

    if not data["nationality"]:

        data["nationality"] = find_labeled_value(
            cleaned_texts,
            [
                "NATIONALITY"
            ]
        )


    # ------------------------------------------------------
    # DOB
    # ------------------------------------------------------

    if not data["date_of_birth"]:

        data["date_of_birth"] = find_date_after_label(
            cleaned_texts,
            [
                "DATE OF BIRTH",
                "DOB",
                "BIRTH DATE"
            ]
        )


    # ------------------------------------------------------
    # Expiry
    # ------------------------------------------------------

    if not data["date_of_expiry"]:

        data["date_of_expiry"] = find_date_after_label(
            cleaned_texts,
            [
                "DATE OF EXPIRY",
                "EXPIRY DATE",
                "EXPIRATION DATE",
                "VALID UNTIL"
            ]
        )


    # ------------------------------------------------------
    # Gender
    # ------------------------------------------------------

    if not data["gender"]:

        data["gender"] = find_labeled_value(
            cleaned_texts,
            [
                "GENDER",
                "SEX"
            ]
        )


    # ------------------------------------------------------
    # Normalize gender
    # ------------------------------------------------------

    if data["gender"]:

        gender = normalized_text(
            data["gender"]
        )

        if gender in [
            "MALE",
            "M"
        ]:

            data["gender"] = "M"

        elif gender in [
            "FEMALE",
            "F"
        ]:

            data["gender"] = "F"


    # ------------------------------------------------------
    # Add raw OCR
    # ------------------------------------------------------

    data["raw_text"] = cleaned_texts


    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    print("\n")
    print("=" * 60)
    print("FINAL EXTRACTED DOCUMENT DATA")
    print("=" * 60)

    print(
        "Document Type   :",
        data["document_type"]
    )

    print(
        "Name            :",
        data["name"]
    )

    print(
        "Document Number :",
        data["document_number"]
    )

    print(
        "Nationality     :",
        data["nationality"]
    )

    print(
        "Date of Birth   :",
        data["date_of_birth"]
    )

    print(
        "Date of Expiry  :",
        data["date_of_expiry"]
    )

    print(
        "Gender          :",
        data["gender"]
    )

    print("=" * 60)


    return data