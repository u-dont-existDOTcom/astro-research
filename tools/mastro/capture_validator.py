"""Read-only validation of captured Mastro birth fields and standard longitudes.

No UI access, no keyword scoring and no search over birth times. Ordinary
validation compares the two explicit captured-time interpretations. A supplied
record may additionally bind an actual application-reported UTC observation.
Swiss Ephemeris is imported only by the numerical comparison function.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re
import unicodedata

MONTHS = {name: number for number, name in enumerate(
    ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
     "septembre", "octobre", "novembre", "decembre"], 1)}
BODY_NAMES = {
    "☉": "Sun", "☽": "Moon", "☿": "Mercury", "♀": "Venus", "♂": "Mars",
    "♃": "Jupiter", "♄": "Saturn", "♅": "Uranus", "♆": "Neptune", "♇": "Pluto",
}


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.casefold())
                   if unicodedata.category(c) != "Mn").strip()


def _edit(field):
    return ".EDIT." in field["cls"]


def _anchor(fields, text):
    matches = [f for f in fields if f.get("text", "").strip() == text]
    if len(matches) != 1:
        raise ValueError(f"Expected one label {text!r}; found {len(matches)}")
    return matches[0]


def _below(fields, anchor, predicate):
    candidates = [f for f in fields if predicate(f)
                  and 8 <= f["y"] - anchor["y"] <= 35
                  and abs((f["x"] + f["w"] / 2) - (anchor["x"] + anchor["w"] / 2)) < 65]
    if not candidates:
        raise ValueError(f"No input under {anchor['text']!r}")
    candidates.sort(key=lambda f: abs((f["x"] + f["w"] / 2) - (anchor["x"] + anchor["w"] / 2)))
    if len(candidates) > 1 and candidates[0]["x"] == candidates[1]["x"]:
        raise ValueError("Ambiguous overlapping controls")
    return candidates[0]["text"].strip()


def _coordinate(fields, directions):
    hemispheres = [f for f in fields if _edit(f) and f.get("text", "").strip().upper() in directions]
    if len(hemispheres) != 1:
        raise ValueError(f"Expected one coordinate hemisphere in {directions}")
    hemisphere = hemispheres[0]
    siblings = sorted([f for f in fields if f["parent"] == hemisphere["parent"]
                       and _edit(f) and re.fullmatch(r"\d+", f.get("text", "").strip())], key=lambda f: f["x"])
    if len(siblings) != 3:
        raise ValueError("Expected coordinate degrees, minutes and seconds")
    degrees, minutes, seconds = [int(f["text"]) for f in siblings]
    if not (0 <= minutes < 60 and 0 <= seconds < 60):
        raise ValueError("Invalid coordinate minutes/seconds")
    sign = -1 if hemisphere["text"].strip().upper() in {"S", "W", "O"} else 1
    value = sign * (degrees + minutes / 60 + seconds / 3600)
    if abs(value) > (90 if "N" in directions else 180):
        raise ValueError("Invalid coordinate magnitude")
    return {"degrees": value, "dms": [degrees, minutes, seconds], "hemisphere": hemisphere["text"].strip()}


def parse_visible_fields(fields):
    """Parse semantic labels and parented coordinate controls, not volatile handles."""
    year = int(_below(fields, _anchor(fields, "Année"), _edit))
    month_text = _below(fields, _anchor(fields, "Mois"), lambda f: ".COMBOBOX." in f["cls"])
    try:
        month = MONTHS[normalize(month_text)]
    except KeyError as error:
        raise ValueError(f"Unknown French month {month_text!r}") from error
    day = int(_below(fields, _anchor(fields, "Jour"), _edit))
    times = [f["text"].strip() for f in fields if "SysDateTimePick32" in f["cls"]]
    if len(times) != 1 or not re.fullmatch(r"\d{2}:\d{2}:\d{2}", times[0]):
        raise ValueError("Expected exactly one captured HH:MM:SS time control")
    local = datetime.fromisoformat(f"{year:04d}-{month:02d}-{day:02d}T{times[0]}")
    anchor = _anchor(fields, "Différence de temps avec GMT:")
    offsets = [f for f in fields if _edit(f) and abs(f["y"] - anchor["y"]) <= 8
               and anchor["x"] + 100 <= f["x"] <= anchor["x"] + 250
               and re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", f.get("text", "").strip())]
    if len(offsets) != 1:
        raise ValueError("Expected exactly one numeric GMT-offset field")
    offset_text = offsets[0]["text"].strip()
    seconds = Decimal(offset_text.replace(",", ".")) * 3600
    if abs(seconds) > 86400:
        raise ValueError("GMT offset outside one day")
    latitude = _coordinate(fields, {"N", "S"})
    longitude = _coordinate(fields, {"E", "W", "O"})
    name_anchor = _anchor(fields, "Nom:")
    names = [f for f in fields if _edit(f) and abs(f["y"] - name_anchor["y"]) <= 8
             and name_anchor["x"] < f["x"] < name_anchor["x"] + 100]
    return {
        "date": local.date().isoformat(), "time": local.time().isoformat(),
        "displayed_datetime": local.isoformat(), "french_month_text": month_text,
        "gmt_offset_hours_text": offset_text, "gmt_offset_seconds": float(seconds),
        "latitude": latitude, "longitude": longitude,
        "name": names[0]["text"] if len(names) == 1 else None,
        "local_utc_candidate": (local - timedelta(microseconds=int(seconds * 1000000))).isoformat() + "Z",
        "tu_utc_candidate": local.isoformat() + "Z",
        "time_radio_state": "not_mechanically_observed",
    }


def parse_standard_longitudes(text):
    """Read absolute tropical longitudes from column 4 of the captured table."""
    positions = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 5 or cells[2] not in BODY_NAMES:
            continue
        symbol = cells[2]
        if symbol in positions:
            raise ValueError(f"Duplicate standard longitude for {symbol}")
        match = re.fullmatch(r"(\d+)°\s*(\d+)'\s*(\d+)\"", cells[4])
        if not match:
            raise ValueError(f"Malformed absolute longitude {cells[4]!r}")
        degrees, minutes, seconds = map(int, match.groups())
        if not (0 <= degrees < 360 and 0 <= minutes < 60 and 0 <= seconds <= 60):
            raise ValueError("Standard longitude out of range")
        # Mastro can round its last displayed second to 60 without carrying
        # into minutes. Normalize only this
        # presentation boundary; coordinate inputs retain strict <60 checks.
        positions[symbol] = ((degrees * 3600 + minutes * 60 + seconds) % (360 * 3600)) / 3600
    if set(positions) != set(BODY_NAMES):
        raise ValueError("Expected all ten physical planets, including Sun and Moon")
    return positions


def angular_error_degrees(a, b):
    return abs((a - b + 180) % 360 - 180)


def compare_positions(utc_iso, longitudes, threshold_degrees=0.01):
    """Compare geocentric apparent tropical longitudes using installed Swiss code.

    The actual returned ephemeris flag is reported: absent Swiss data files may
    cause its documented Moshier fallback. Nodes/houses are deliberately outside
    this check. Geocentric longitudes do not independently verify coordinates.
    """
    import swisseph as swe
    time = datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    hour = time.hour + time.minute / 60 + (time.second + time.microsecond / 1000000) / 3600
    jd = swe.julday(time.year, time.month, time.day, hour, swe.GREG_CAL)
    bodies = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER,
              swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO]
    details = {}
    for (symbol, name), body in zip(BODY_NAMES.items(), bodies):
        values, returned_flags = swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)
        error = angular_error_degrees(values[0], longitudes[symbol])
        details[name] = {"captured_degrees": longitudes[symbol], "independent_degrees": values[0],
                         "absolute_error_degrees": error, "passed": error <= threshold_degrees,
                         "returned_flags": returned_flags,
                         "ephemeris": "Moshier" if returned_flags & swe.FLG_MOSEPH else "Swiss" if returned_flags & swe.FLG_SWIEPH else "JPL_or_other"}
    return {"utc_candidate": utc_iso, "passed": all(v["passed"] for v in details.values()),
            "sun_moon_passed": details["Sun"]["passed"] and details["Moon"]["passed"],
            "threshold_degrees": threshold_degrees, "swisseph_version": swe.version,
            "maximum_error_degrees": max(v["absolute_error_degrees"] for v in details.values()),
            "planets": details}


def compare_expected(captured, expected, entry_mode="source_local", utc_tolerance_seconds=0.01,
                     coordinate_tolerance_degrees=1 / 3600):
    """Compare against a recovered-source record or a source-local expectation.

    UTC reconstruction mode requires the *visible* fields to contain the source
    UTC instant with zero offset, including any date rollover. It retains source
    local fields in the result and never substitutes the current local date.
    """
    source = expected["published_inputs"]
    derived = expected["derived_inputs"]
    if entry_mode not in {"source_local", "utc_reconstruction"}:
        raise ValueError("Unknown entry mode")
    intended = datetime.fromisoformat(derived["utc_instant"].replace("Z", "+00:00"))
    if entry_mode == "utc_reconstruction":
        intended_display = intended.replace(tzinfo=None)
        expected_offset = 0
    else:
        intended_display = datetime.fromisoformat(source["birth_date"] + "T" + source["local_time"])
        expected_offset = derived["utc_offset_seconds"]
    display = datetime.fromisoformat(captured["displayed_datetime"])
    checks = {
        "date": display.date() == intended_display.date(),
        "displayed_time": abs((display - intended_display).total_seconds()) <= utc_tolerance_seconds,
        "offset": abs(captured["gmt_offset_seconds"] - expected_offset) <= utc_tolerance_seconds,
        "latitude": abs(captured["latitude"]["degrees"] - derived["latitude_degrees"]) <= coordinate_tolerance_degrees,
        "longitude": abs(captured["longitude"]["degrees"] - derived["longitude_degrees"]) <= coordinate_tolerance_degrees,
    }
    captured_utc = datetime.fromisoformat(captured["local_utc_candidate"].replace("Z", "+00:00"))
    checks["source_derived_utc"] = abs((captured_utc - intended).total_seconds()) <= utc_tolerance_seconds
    return {"passed": all(checks.values()), "checks": checks, "entry_mode": entry_mode,
            "source_local_date": source["birth_date"], "source_local_time": source["local_time"],
            "source_reference_meridian": source["reference_meridian_source"],
            "source_derived_utc": derived["utc_instant"],
            "captured_local_hypothesis_minus_source_utc_seconds": (captured_utc - intended).total_seconds(),
            "latitude_difference_degrees": captured["latitude"]["degrees"] - derived["latitude_degrees"],
            "longitude_difference_degrees": captured["longitude"]["degrees"] - derived["longitude_degrees"],
            "source_status": expected.get("status"), "source_uncertainty": expected.get("uncertainty"),
            "historical_equivalence": expected.get("historical_equivalence", {"status": "unverified"})}


def validate_observed_utc_exception(document, captured):
    """Bind a saved app-reported clock to this exact supplied-record capture.

    This verifies consistency of saved STATIC evidence, not clock truth,
    historical equivalence, or the unresolved source time convention.
    """
    if document.get("provenance") != "supplied_mastro_database":
        raise ValueError("Observed-UTC exceptions are forbidden for reconstructed inputs")
    exception = document["observed_utc_exception"]
    if not isinstance(exception, dict) or exception.get("schema") != 1:
        raise ValueError("Invalid observed-UTC exception schema")
    if exception.get("status") != "unresolved_supplied_record_time_convention":
        raise ValueError("Observed-UTC exception must retain unresolved-convention status")
    if not document.get("subject_id") or exception.get("subject_id") != document["subject_id"]:
        raise ValueError("Observed-UTC exception subject binding mismatch")
    required_bindings = {
        "captured_source_name": captured["name"],
        "captured_local_datetime": captured["displayed_datetime"],
        "captured_offset_hours_text": captured["gmt_offset_hours_text"],
    }
    if not captured["name"] or any(exception.get(key) != value for key, value in required_bindings.items()):
        raise ValueError("Observed-UTC exception captured-source binding mismatch")
    raw = exception.get("raw_main_controls")
    main_fields = exception.get("main_fields")
    if not isinstance(raw, list) or not isinstance(main_fields, dict):
        raise ValueError("Observed-UTC exception requires raw main STATIC evidence")
    statics = [field for field in raw if ".STATIC." in field.get("cls", "")]
    recovered = {}
    anchors = {label: _anchor(statics, label) for label in ["Nom:", "Date:", "Heure:", "TU:"]}
    parents = {anchor.get("parent") for anchor in anchors.values()}
    if len(parents) != 1 or not next(iter(parents)):
        raise ValueError("Observed main labels must belong to one captured panel")
    for label, anchor in anchors.items():
        values = [field for field in statics if field.get("parent") == anchor.get("parent")
                  and field.get("handle") != anchor.get("handle")
                  and abs(field["y"] - anchor["y"]) <= 1
                  and anchor["x"] + anchor["w"] <= field["x"] <= anchor["x"] + 600]
        if len(values) != 1:
            raise ValueError(f"Missing or ambiguous raw main value for {label}")
        recovered[label] = values[0]["text"]
        if main_fields.get(label) != recovered[label]:
            raise ValueError(f"Raw main-panel binding mismatch for {label}")
    if recovered["Nom:"] != captured["name"]:
        raise ValueError("Observed main name differs from captured source name")
    if recovered["Date:"] != captured["date"].replace("-", "/") or recovered["Heure:"] != captured["time"]:
        raise ValueError("Observed main local date/time differs from captured source")
    reported = exception.get("reported_utc", "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", reported):
        raise ValueError("Observed main UTC must be an exact UTC datetime")
    reported_time = datetime.fromisoformat(reported.replace("Z", "+00:00"))
    tu_match = re.fullmatch(r"(\d{2}:\d{2}:\d{2}) \((\d{1,2})/(\d{1,2})\)", recovered["TU:"])
    if not tu_match:
        raise ValueError("Unrecognized observed main TU clock/date presentation")
    clock, month, day = tu_match.groups()
    if clock != reported_time.time().isoformat() or (int(month), int(day)) != (reported_time.month, reported_time.day):
        raise ValueError("Observed UTC differs from raw main TU clock/date")
    local_date = datetime.fromisoformat(captured["displayed_datetime"]).date()
    if abs((reported_time.date() - local_date).days) > 1:
        raise ValueError("Observed UTC year/date is not bound to the captured civil date")
    observation = datetime.fromisoformat(exception["observed_utc"].replace("Z", "+00:00"))
    if observation.tzinfo is None or observation.utcoffset() != timedelta(0):
        raise ValueError("Observation timestamp must explicitly use UTC")
    return {"reported_utc": reported, "binding_checks_passed": True,
            "status": "reported_utc_verified_source_convention_unresolved",
            "main_fields": recovered, "raw_main_controls": raw,
            "observed_utc": exception["observed_utc"], "subject_id": exception["subject_id"],
            "captured_source_bindings": required_bindings,
            "scope": "Observed application clock only; no true-birth-time or historical-equivalence claim."}


def validate_capture(input_document, standard_positions_text, expected=None,
                     entry_mode="source_local", threshold_degrees=0.01):
    captured = parse_visible_fields(input_document["visible_fields"])
    observed = validate_observed_utc_exception(input_document, captured) if "observed_utc_exception" in input_document else None
    longitudes = parse_standard_longitudes(standard_positions_text)
    hypotheses = {mode: compare_positions(captured[key], longitudes, threshold_degrees)
                  for mode, key in [("local", "local_utc_candidate"), ("TU", "tu_utc_candidate")]}
    matches = [mode for mode, result in hypotheses.items() if result["passed"]]
    same_instant = captured["local_utc_candidate"] == captured["tu_utc_candidate"]
    supported = hypotheses[matches[0]]["utc_candidate"] if matches and (len(matches) == 1 or same_instant) else None
    source_comparison = compare_expected(captured, expected, entry_mode) if expected else None
    status = "position_consistency_verified" if matches else "position_mismatch"
    if matches and source_comparison and not source_comparison["passed"]:
        status = "source_input_mismatch" if entry_mode == "utc_reconstruction" else "review_required_source_discrepancy"
    raw_matches = matches[:]
    ambiguity = "same_instant_no_effect" if len(matches) == 2 and same_instant else "distinct_instants_both_fit" if len(matches) == 2 else "none" if len(matches) == 1 else "no_interpretation_fits"
    discrepancy = None
    if observed:
        # The two raw-offset interpretations remain diagnostic results. The
        # exceptional gate compares only the actually reported, bound app UTC.
        hypothesis = compare_positions(observed["reported_utc"], longitudes, threshold_degrees)
        hypotheses["observed_app_UTC"] = hypothesis
        matches = ["observed_app_UTC"] if hypothesis["passed"] else []
        supported = observed["reported_utc"] if matches else None
        status = observed["status"] if matches else "position_mismatch"
        ambiguity = "observed_app_utc_bound_radio_unobserved" if matches else "no_interpretation_fits"
        observed_time = datetime.fromisoformat(observed["reported_utc"].replace("Z", "+00:00"))
        discrepancy = {"flag": "supplied_record_time_convention_unresolved",
                       "observed_app_minus_local_offset_hypothesis_seconds": (observed_time - datetime.fromisoformat(captured["local_utc_candidate"].replace("Z", "+00:00"))).total_seconds(),
                       "observed_app_minus_tu_hypothesis_seconds": (observed_time - datetime.fromisoformat(captured["tu_utc_candidate"].replace("Z", "+00:00"))).total_seconds(),
                       "raw_hypotheses_matching_positions": raw_matches,
                       "interpretation": "The application-reported UTC is checked as observed. The captured source offset convention remains unresolved."}
    return {"schema": 1, "subject_id": input_document.get("subject_id"), "status": status,
            "captured": captured, "position_hypotheses": hypotheses,
            "matching_time_interpretations": matches, "hypotheses_are_same_instant": same_instant,
            "effective_utc_supported_by_positions": supported,
            "time_mode_ambiguity": ambiguity,
            "observed_utc_evidence": observed, "source_convention_discrepancy": discrepancy,
            "time_mode_evidence": "Position comparison is diagnostic evidence, not observation of the unreadable radio state.",
            "coordinates_evidence": "Compared directly to expected source fields when supplied; geocentric planets do not verify coordinates.",
            "expected_source_comparison": source_comparison,
            "keyword_scores_used": False}


def group_source_uncertainty(inputs_document):
    """Keep the existing source-review population separate from capture checks."""
    groups = {"verified_source": [], "review_required": [], "missing": []}
    flags = {}
    for record in inputs_document["records"]:
        groups[record["status"]].append(record["subject_id"])
        for flag in record["uncertainty"]["flags"]:
            flags.setdefault(flag, []).append(record["subject_id"])
    return {"by_status": groups, "by_flag": flags,
            "note": "A capture/ephemeris pass does not resolve source uncertainty or historical equivalence."}
