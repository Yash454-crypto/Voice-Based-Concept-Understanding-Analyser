"""
Performance Testing & Optimization Demo
-------------------------------------------
Run with:  python performance_app.py        (standalone benchmark report)
       or: streamlit run performance_app.py  (interactive dashboard)

Demonstrates:
- Benchmarking with `timeit` / manual timing decorators
- Profiling with `cProfile` + `pstats`
- Memory profiling (tracemalloc, no extra deps)
- Optimization techniques compared head-to-head:
    * Python loop vs list comprehension vs NumPy vectorization
    * String concatenation: += vs join
    * Caching (memoization) vs recomputation
    * Streamlit st.cache_data vs uncached function
- A simple load-test style benchmark for a function under repeated calls
- Producing a results table + bar chart of relative speedups

Dependencies:
    pip install streamlit pandas numpy matplotlib
"""

import time
import cProfile
import pstats
import io
import tracemalloc
from functools import lru_cache, wraps

import numpy as np
import pandas as pd

# ============================================================================
# SECTION 1: Timing utilities
# ============================================================================

def time_it(func, *args, repeats: int = 5, **kwargs):
    """Run func `repeats` times, return (avg_seconds, result_of_last_call)."""
    durations = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        durations.append(time.perf_counter() - start)
    return sum(durations) / len(durations), result


def timing_decorator(func):
    """Decorator that prints execution time of a function call."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timing] {func.__name__} took {elapsed * 1000:.3f} ms")
        return result
    return wrapper


# ============================================================================
# SECTION 2: Optimization comparison — loops vs comprehension vs NumPy
# ============================================================================

def squares_loop(n):
    result = []
    for i in range(n):
        result.append(i * i)
    return result


def squares_comprehension(n):
    return [i * i for i in range(n)]


def squares_numpy(n):
    arr = np.arange(n)
    return arr * arr


def benchmark_squares(n=200_000, repeats=5):
    rows = []
    for name, func in [
        ("for-loop", squares_loop),
        ("list comprehension", squares_comprehension),
        ("numpy vectorized", squares_numpy),
    ]:
        avg_time, _ = time_it(func, n, repeats=repeats)
        rows.append({"method": name, "avg_seconds": avg_time})
    df = pd.DataFrame(rows)
    baseline = df["avg_seconds"].max()
    df["speedup_vs_slowest"] = (baseline / df["avg_seconds"]).round(1)
    return df


# ============================================================================
# SECTION 3: String building — += vs join
# ============================================================================

def build_string_concat(n):
    s = ""
    for i in range(n):
        s += str(i)
    return s


def build_string_join(n):
    return "".join(str(i) for i in range(n))


def benchmark_strings(n=20_000, repeats=5):
    rows = []
    for name, func in [
        ("string += in loop", build_string_concat),
        ("''.join() generator", build_string_join),
    ]:
        avg_time, _ = time_it(func, n, repeats=repeats)
        rows.append({"method": name, "avg_seconds": avg_time})
    df = pd.DataFrame(rows)
    baseline = df["avg_seconds"].max()
    df["speedup_vs_slowest"] = (baseline / df["avg_seconds"]).round(1)
    return df


# ============================================================================
# SECTION 4: Caching / memoization
# ============================================================================

def fib_uncached(n):
    if n < 2:
        return n
    return fib_uncached(n - 1) + fib_uncached(n - 2)


@lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def benchmark_fibonacci(n=27, repeats=3):
    rows = []
    avg_uncached, _ = time_it(fib_uncached, n, repeats=repeats)
    rows.append({"method": "fibonacci (no cache)", "avg_seconds": avg_uncached})

    fib_cached.cache_clear()
    # First call populates the cache; time only the *first* call cost once,
    # then show that subsequent calls are ~free.
    start = time.perf_counter()
    fib_cached(n)
    first_call = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(repeats):
        fib_cached(n)
    cached_avg = (time.perf_counter() - start) / repeats

    rows.append({"method": "fibonacci (lru_cache, first call)", "avg_seconds": first_call})
    rows.append({"method": "fibonacci (lru_cache, cached calls)", "avg_seconds": cached_avg})

    df = pd.DataFrame(rows)
    baseline = df["avg_seconds"].max()
    df["speedup_vs_slowest"] = (baseline / df["avg_seconds"].replace(0, 1e-9)).round(1)
    return df


# ============================================================================
# SECTION 5: cProfile-based profiling
# ============================================================================

def expensive_pipeline(n=50_000):
    """A toy pipeline with multiple stages, useful to profile for hotspots."""
    data = [i for i in range(n)]
    data = [x * 2 for x in data]
    total = sum(x for x in data if x % 3 == 0)
    sorted_subset = sorted(data[:1000], reverse=True)
    return total, sorted_subset[:5]


def profile_function(func, *args, top_n=8, **kwargs):
    """Run cProfile on func and return a readable stats string."""
    profiler = cProfile.Profile()
    profiler.enable()
    func(*args, **kwargs)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(top_n)
    return stream.getvalue()


# ============================================================================
# SECTION 6: Memory profiling with tracemalloc
# ============================================================================

def measure_memory(func, *args, **kwargs):
    """Return (peak_memory_kb, result) for a function call."""
    tracemalloc.start()
    result = func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024, result  # KB


def compare_memory_usage():
    rows = []
    for label, func, n in [
        ("list of 1M ints", lambda: list(range(1_000_000)), None),
        ("numpy array of 1M ints", lambda: np.arange(1_000_000), None),
        ("generator (lazy, not materialized)", lambda: (i for i in range(1_000_000)), None),
    ]:
        peak_kb, _ = measure_memory(func)
        rows.append({"structure": label, "peak_kb": round(peak_kb, 1)})
    return pd.DataFrame(rows)


# ============================================================================
# SECTION 7: Simple repeated-call "load test"
# ============================================================================

def load_test(func, *args, calls: int = 100, **kwargs):
    """Call func repeatedly and report latency stats — a lightweight
    stand-in for load testing a function (e.g. a request handler)."""
    durations = []
    for _ in range(calls):
        start = time.perf_counter()
        func(*args, **kwargs)
        durations.append((time.perf_counter() - start) * 1000)  # ms

    arr = np.array(durations)
    return {
        "calls": calls,
        "avg_ms": round(arr.mean(), 3),
        "p50_ms": round(np.percentile(arr, 50), 3),
        "p95_ms": round(np.percentile(arr, 95), 3),
        "p99_ms": round(np.percentile(arr, 99), 3),
        "max_ms": round(arr.max(), 3),
    }


# ============================================================================
# SECTION 8: Standalone CLI report (runs without Streamlit)
# ============================================================================

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def run_cli_report():
    print_section("1. Loop vs Comprehension vs NumPy (computing squares)")
    print(benchmark_squares().to_string(index=False))

    print_section("2. String concatenation: += vs join")
    print(benchmark_strings().to_string(index=False))

    print_section("3. Memoization: fib(27) cached vs uncached")
    print(benchmark_fibonacci().to_string(index=False))

    print_section("4. cProfile hotspot report: expensive_pipeline()")
    print(profile_function(expensive_pipeline, 50_000))

    print_section("5. Memory usage comparison (peak KB)")
    print(compare_memory_usage().to_string(index=False))

    print_section("6. Load test: repeated calls to squares_numpy(10000)")
    stats = load_test(squares_numpy, 10_000, calls=200)
    for k, v in stats.items():
        print(f"  {k}: {v}")


# ============================================================================
# SECTION 9: Optional Streamlit dashboard (only runs under `streamlit run`)
# ============================================================================

def run_streamlit_dashboard():
    import streamlit as st
    import matplotlib.pyplot as plt

    st.set_page_config(page_title="Performance Testing & Optimization", page_icon="⚡", layout="wide")
    st.title("⚡ Performance Testing & Optimization")
    st.caption("Benchmark, profile, and compare optimization strategies interactively.")

    def show_bar(df, value_col, label_col, title):
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.barh(df[label_col], df[value_col], color="#6366f1")
        ax.set_xlabel(value_col)
        ax.set_title(title)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        st.pyplot(fig)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Loop vs Vectorized", "String Building", "Caching", "Profiling", "Memory", "Load Test"]
    )

    with tab1:
        st.subheader("Computing squares: loop vs comprehension vs NumPy")
        n = st.slider("Array size", 10_000, 1_000_000, 200_000, step=10_000, key="sq_n")
        if st.button("Run benchmark", key="bench_squares"):
            df = benchmark_squares(n=n)
            st.dataframe(df, use_container_width=True)
            show_bar(df, "avg_seconds", "method", "Average time (s)")

    with tab2:
        st.subheader("String concatenation: += vs join")
        n = st.slider("Number of strings", 1_000, 100_000, 20_000, step=1_000, key="str_n")
        if st.button("Run benchmark", key="bench_strings"):
            df = benchmark_strings(n=n)
            st.dataframe(df, use_container_width=True)
            show_bar(df, "avg_seconds", "method", "Average time (s)")

    with tab3:
        st.subheader("Memoization with lru_cache")
        n = st.slider("Fibonacci n", 20, 32, 27, key="fib_n")
        if st.button("Run benchmark", key="bench_fib"):
            df = benchmark_fibonacci(n=n)
            st.dataframe(df, use_container_width=True)
            show_bar(df, "avg_seconds", "method", "Average time (s)")

        st.markdown("---")
        st.write("**Streamlit's own caching** (`st.cache_data`) works the same way: "
                  "the first call computes and stores; subsequent calls with the same "
                  "arguments return instantly from cache.")

    with tab4:
        st.subheader("cProfile hotspot report")
        pipeline_n = st.slider("Pipeline size", 10_000, 200_000, 50_000, step=10_000)
        if st.button("Profile pipeline"):
            report = profile_function(expensive_pipeline, pipeline_n)
            st.code(report, language="text")

    with tab5:
        st.subheader("Peak memory usage by data structure")
        if st.button("Measure memory"):
            df = compare_memory_usage()
            st.dataframe(df, use_container_width=True)
            show_bar(df, "peak_kb", "structure", "Peak memory (KB)")

    with tab6:
        st.subheader("Repeated-call load test")
        calls = st.slider("Number of calls", 10, 1000, 200, step=10)
        if st.button("Run load test"):
            stats = load_test(squares_numpy, 10_000, calls=calls)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Avg (ms)", stats["avg_ms"])
            col2.metric("P50 (ms)", stats["p50_ms"])
            col3.metric("P95 (ms)", stats["p95_ms"])
            col4.metric("P99 (ms)", stats["max_ms"])
            st.json(stats)


# ============================================================================
# Entry point: detect whether running under `streamlit run` or plain `python`
# ============================================================================

def _running_under_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if _running_under_streamlit():
    run_streamlit_dashboard()
elif __name__ == "__main__":
    run_cli_report()