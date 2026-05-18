import json
from openpyxl import Workbook

pit_values = [500, 240, 120, 60, 30, 15, 7]

wb = Workbook()
wb.remove(wb.active)

for num_pit in pit_values:
    # Load files
    with open(f"results/bf/results_pit_{num_pit}.json", "r") as f:
        correct = json.load(f)

    with open(f"results/approx/approx_pit_{num_pit}.json", "r") as f:
        approx = json.load(f)

    with open(f"results/dp/results_pit_{num_pit}.json", "r") as f:
        dp = json.load(f)

    with open(f"results/pdp/results_pit_{num_pit}.json", "r") as f:
        par = json.load(f)

    if num_pit == 15 or num_pit == 7:
        with open(f"results/mip/results_pit_{num_pit}.json", "r") as f:
            mip = json.load(f)

    # Maps
    correct_map = {d["board_index"]: d for d in correct}
    approx_map = {d["board_index"]: d for d in approx}

    total = len(correct_map)
    match_count = 0
    differences = []
    mismatches = []

    correct_times = []
    approx_times = []

    # =============================
    # SECTION 1 — ACCURACY
    # =============================
    for i in correct_map:
        c_data = correct_map[i]
        a_data = approx_map.get(i)

        if a_data is None:
            continue  # skip if missing in approx

        c = c_data.get("max_seeds", 0)
        a = a_data.get("max_seeds", 0)

        if c == a:
            match_count += 1
        else:
            mismatches.append((
                str(c_data.get("initial_board")),
                i,  # board_index
                c,
                a,
                c - a,
                str(c_data.get("best_sequence")),
                str(a_data.get("best_sequence"))
            ))

        differences.append(c - a)

        correct_times.append(c_data.get("execution_time_ms", 0))
        approx_times.append(a_data.get("execution_time_ms", 0))

    accuracy = (match_count / total * 100) if total > 0 else 0
    avg_error = (sum(differences) / total) if total > 0 else 0

    avg_correct_time = sum(correct_times) / len(correct_times) if correct_times else 0
    avg_approx_time = sum(approx_times) / len(approx_times) if approx_times else 0

    total_correct_time = sum(correct_times)
    total_approx_time = sum(approx_times)

    # Top 5 slowest BF
    slowest_bf = sorted(correct, key=lambda x: x.get("execution_time_ms", 0), reverse=True)[:5]

    # =============================
    # SECTION 2 — DP
    # =============================
    dp_times = [d.get("execution_time_ms", 0) for d in dp]
    dp_avg = sum(dp_times) / len(dp_times) if dp_times else 0
    dp_total = sum(dp_times)

    slowest_dp = sorted(dp, key=lambda x: x.get("execution_time_ms", 0), reverse=True)[:5]

    # =============================
    # SECTION 3 — PARALLEL
    # =============================
    par_times = [d.get("execution_time_ms", 0) for d in par]
    par_avg = sum(par_times) / len(par_times) if par_times else 0
    par_total = sum(par_times)

    slowest_par = sorted(par, key=lambda x: x.get("execution_time_ms", 0), reverse=True)[:5]

    # =============================
    # SECTION 4 — MIP
    # =============================
    if num_pit == 7 or num_pit == 15:
        mip_times = [d.get("execution_time_ms", 0) for d in mip]
        mip_avg = sum(mip_times) / len(mip_times) if mip_times else 0
        mip_total = sum(mip_times)

        slowest_mip = sorted(mip, key=lambda x: x.get("execution_time_ms", 0), reverse=True)[:5]

    # =============================
    # WRITE TO EXCEL
    # =============================
    ws = wb.create_sheet(title=f"pit_{num_pit}")

    # -------- SECTION 1 --------
    ws.append(["SECTION 1 — ACCURACY (BF vs APPROX)"])
    ws.append([])

    ws.append(["Total Sequences", total])
    ws.append(["Accuracy (%)", accuracy])
    ws.append(["Average Error", avg_error])
    ws.append(["Avg BF Time (ms)", avg_correct_time])
    ws.append(["Avg Approx Time (ms)", avg_approx_time])
    ws.append(["Total BF Time (s)", total_correct_time / 1000])
    ws.append(["Total Approx Time (s)", total_approx_time / 1000])

    ws.append([])
    ws.append([])

    # Top 5 BF
    ws.append(["Top 5 Slowest (BF)"])
    ws.append(["initial_board", "board_index", "execution_time_ms", "max_seeds", "sequence"])

    for item in slowest_bf:
        ws.append([
            str(item.get("initial_board")),
            item.get("board_index"),
            item.get("execution_time_ms"),
            item.get("max_seeds"),
            str(item.get("best_sequence"))
        ])

    ws.append([])
    ws.append([])

    # Mismatches
    ws.append(["MISMATCHES"])
    ws.append([
        "initial_board",
        "board_index",
        "correct_max_seeds",
        "approx_max_seeds",
        "difference",
        "correct_sequence",
        "approx_sequence"
    ])

    for m in mismatches:
        ws.append(m)

    ws.append([])
    ws.append([])

    # -------- SECTION 2 --------
    ws.append(["SECTION 2 — DP PERFORMANCE"])
    ws.append([])

    ws.append(["Avg Time (ms)", dp_avg])
    ws.append(["Total Time (s)", dp_total / 1000])

    ws.append([])
    ws.append(["Top 5 Slowest (DP)"])
    ws.append(["initial_board", "execution_time_ms", "max_seeds", "sequence"])

    for item in slowest_dp:
        ws.append([
            str(item.get("initial_board")),
            item.get("execution_time_ms"),
            item.get("max_seeds"),
            str(item.get("best_sequence"))
        ])

    ws.append([])
    ws.append([])

    # -------- SECTION 3 --------
    ws.append(["SECTION 3 — PARALLEL PERFORMANCE"])
    ws.append([])

    ws.append(["Avg Time (ms)", par_avg])
    ws.append(["Total Time (s)", par_total / 1000])

    ws.append([])
    ws.append(["Top 5 Slowest (Parallel)"])
    ws.append(["initial_board", "execution_time_ms", "max_seeds", "sequence"])

    for item in slowest_par:
        ws.append([
            str(item.get("initial_board")),
            item.get("execution_time_ms"),
            item.get("max_seeds"),
            str(item.get("best_sequence"))
        ])

    ws.append([])
    ws.append([])

    # -------- SECTION 4 --------
    if num_pit == 7 or num_pit == 15:
        ws.append(["SECTION 4 — MIP PERFORMANCE"])
        ws.append([])

        ws.append(["Avg Time (ms)", mip_avg])
        ws.append(["Total Time (s)", mip_total / 1000])

        ws.append([])
        ws.append(["Top 5 Slowest (MIP)"])
        ws.append(["initial_board", "execution_time_ms", "max_seeds", "sequence"])

        for item in slowest_mip:
            ws.append([
                str(item.get("initial_board")),
                item.get("execution_time_ms"),
                item.get("max_seeds"),
                str(item.get("best_sequence"))
            ])

# Save file
output_file = "analysis/final_analysis.xlsx"
wb.save(output_file)

print(f"Saved to {output_file}")