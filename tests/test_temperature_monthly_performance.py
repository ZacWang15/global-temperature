"""Performance tests for TemperatureMonthly class."""
from global_temperature.temperature_monthly import TemperatureMonthly
import pytest
import time
from typing import List, Dict


@pytest.fixture
def monthly_instance():
    """Fixture to set up the TemperatureMonthly instance using 0.1 x 0.1 degrees."""
    temp_monthly = TemperatureMonthly(
        search_radius=0.1,
        geohash_precision=1,
        max_cache_size=100,
        grid_name="01x01",
    )
    return temp_monthly


@pytest.fixture
def test_locations():
    """Common test locations with expected results."""
    return [
        # Melbourne
        {"year": 2024, "month": 1, "latitude": -37.89994, "longitude": 145.06802, "expected": 19.69},
        # New York
        {"year": 2024, "month": 1, "latitude": 40.7128, "longitude": -74.0060, "expected": 1.18},
        # Los Angeles - multiple months
        {"year": 2011, "month": 1, "latitude": 34.0522, "longitude": -118.2437, "expected": 11.59},
        {"year": 2011, "month": 3, "latitude": 34.0522, "longitude": -118.2437, "expected": 12.88},
        {"year": 2011, "month": 6, "latitude": 34.0522, "longitude": -118.2437, "expected": 19.01},
        {"year": 2011, "month": 9, "latitude": 34.0522, "longitude": -118.2437, "expected": 22.57},
        {"year": 2011, "month": 12, "latitude": 34.0522, "longitude": -118.2437, "expected": 10.35},
    ]


class TestSingleQueryPerformance:
    """Test performance of single queries."""

    def test_single_query_timing(self, monthly_instance, test_locations):
        """Measure timing for a single query (cold cache)."""
        location = test_locations[0]  # Melbourne
        
        start_time = time.perf_counter()
        result = monthly_instance.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        print(f"\n[PERFORMANCE] Single query (cold cache): {elapsed_ms:.2f}ms")
        assert result["temperature"] == location["expected"]
        assert elapsed_ms < 1000, f"Single query took too long: {elapsed_ms:.2f}ms"

    def test_repeated_query_timing(self, monthly_instance, test_locations):
        """Measure timing for repeated queries to the same location (cache hit)."""
        location = test_locations[0]  # Melbourne
        
        # First query (cold cache)
        first_start = time.perf_counter()
        monthly_instance.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        first_end = time.perf_counter()
        first_elapsed_ms = (first_end - first_start) * 1000
        
        # Second query (should hit cache)
        second_start = time.perf_counter()
        result = monthly_instance.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        second_end = time.perf_counter()
        second_elapsed_ms = (second_end - second_start) * 1000
        
        print(f"\n[PERFORMANCE] First query (cold): {first_elapsed_ms:.2f}ms")
        print(f"[PERFORMANCE] Second query (cached): {second_elapsed_ms:.2f}ms")
        print(f"[PERFORMANCE] Speedup: {first_elapsed_ms / second_elapsed_ms:.2f}x")
        
        assert result["temperature"] == location["expected"]
        assert second_elapsed_ms < first_elapsed_ms, "Cached query should be faster"


class TestBulkQueryPerformance:
    """Test performance of multiple queries."""

    def test_sequential_queries_timing(self, monthly_instance, test_locations):
        """Measure timing for sequential queries to different locations."""
        timings = []
        
        for location in test_locations:
            start_time = time.perf_counter()
            result = monthly_instance.query(
                year=location["year"],
                month=location["month"],
                latitude=location["latitude"],
                longitude=location["longitude"],
            )
            end_time = time.perf_counter()
            
            elapsed_ms = (end_time - start_time) * 1000
            timings.append(elapsed_ms)
            assert result["temperature"] == location["expected"]
        
        avg_time = sum(timings) / len(timings)
        total_time = sum(timings)
        
        print(f"\n[PERFORMANCE] Sequential queries:")
        print(f"  Total queries: {len(test_locations)}")
        print(f"  Total time: {total_time:.2f}ms")
        print(f"  Average time per query: {avg_time:.2f}ms")
        print(f"  Min time: {min(timings):.2f}ms")
        print(f"  Max time: {max(timings):.2f}ms")
        
        assert avg_time < 500, f"Average query time too high: {avg_time:.2f}ms"

    def test_repeated_location_queries(self, monthly_instance):
        """Test performance with repeated queries to the same location (different times)."""
        # Los Angeles across multiple months
        la_queries = [
            {"year": 2011, "month": 1, "latitude": 34.0522, "longitude": -118.2437},
            {"year": 2011, "month": 3, "latitude": 34.0522, "longitude": -118.2437},
            {"year": 2011, "month": 6, "latitude": 34.0522, "longitude": -118.2437},
            {"year": 2011, "month": 9, "latitude": 34.0522, "longitude": -118.2437},
            {"year": 2011, "month": 12, "latitude": 34.0522, "longitude": -118.2437},
        ]
        
        timings = []
        for query in la_queries:
            start_time = time.perf_counter()
            monthly_instance.query(**query)
            end_time = time.perf_counter()
            timings.append((end_time - start_time) * 1000)
        
        print(f"\n[PERFORMANCE] Repeated location (LA) across months:")
        for i, timing in enumerate(timings, 1):
            print(f"  Query {i}: {timing:.2f}ms")
        
        # Later queries might benefit from caching/optimization
        avg_later = sum(timings[1:]) / len(timings[1:])
        print(f"  Average (excluding first): {avg_later:.2f}ms")


class TestCachePerformance:
    """Test cache performance with different configurations."""

    @pytest.mark.parametrize("cache_size", [10, 50, 100, 200])
    def test_cache_size_impact(self, cache_size, test_locations):
        """Test performance impact of different cache sizes."""
        temp_monthly = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=cache_size,
            grid_name="01x01",
        )
        
        # First pass - populate cache
        for location in test_locations:
            temp_monthly.query(
                year=location["year"],
                month=location["month"],
                latitude=location["latitude"],
                longitude=location["longitude"],
            )
        
        # Second pass - measure cached performance
        start_time = time.perf_counter()
        for location in test_locations:
            temp_monthly.query(
                year=location["year"],
                month=location["month"],
                latitude=location["latitude"],
                longitude=location["longitude"],
            )
        end_time = time.perf_counter()
        
        total_cached_ms = (end_time - start_time) * 1000
        avg_cached_ms = total_cached_ms / len(test_locations)
        
        print(f"\n[PERFORMANCE] Cache size {cache_size}:")
        print(f"  Total cached time: {total_cached_ms:.2f}ms")
        print(f"  Average per query: {avg_cached_ms:.2f}ms")


class TestConfigurationPerformance:
    """Test performance with different configuration parameters."""

    @pytest.mark.parametrize("search_radius", [0.05, 0.1, 0.2, 0.5])
    def test_search_radius_impact(self, search_radius, test_locations):
        """Test performance impact of different search radii."""
        temp_monthly = TemperatureMonthly(
            search_radius=search_radius,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        location = test_locations[0]  # Melbourne
        
        start_time = time.perf_counter()
        temp_monthly.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        print(f"\n[PERFORMANCE] Search radius {search_radius}: {elapsed_ms:.2f}ms")

class TestBenchmarkComparison:
    """Comparative performance tests."""

    def test_cold_vs_warm_cache(self, test_locations):
        """Compare performance between cold and warm cache states."""
        location = test_locations[0]
        
        # Cold cache
        temp_monthly_cold = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        start_cold = time.perf_counter()
        temp_monthly_cold.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        end_cold = time.perf_counter()
        cold_ms = (end_cold - start_cold) * 1000
        
        # Warm cache
        temp_monthly_warm = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        # Pre-warm
        temp_monthly_warm.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        
        start_warm = time.perf_counter()
        temp_monthly_warm.query(
            year=location["year"],
            month=location["month"],
            latitude=location["latitude"],
            longitude=location["longitude"],
        )
        end_warm = time.perf_counter()
        warm_ms = (end_warm - start_warm) * 1000
        
        speedup = cold_ms / warm_ms if warm_ms > 0 else float('inf')
        
        print(f"\n[PERFORMANCE] Cache comparison:")
        print(f"  Cold cache: {cold_ms:.2f}ms")
        print(f"  Warm cache: {warm_ms:.2f}ms")
        print(f"  Speedup: {speedup:.2f}x")
        
        assert warm_ms < cold_ms, "Warm cache should be faster than cold cache"


class TestPreComputedParametersPerformance:
    """Test performance improvement when using pre-computed snapped coordinates and geohash."""

    def test_with_vs_without_precomputed_params_single_query(self):
        """Compare performance of single query with and without pre-computed parameters."""
        temp_monthly = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        # Test data (Melbourne area)
        year = 2024
        month = 1
        latitude = -37.89994
        longitude = 145.06802
        snapped_latitude = -37.900001525878906
        snapped_longitude = 145.10000610351562
        geohash = "r"
        
        # Test WITHOUT pre-computed parameters (standard query)
        start_without = time.perf_counter()
        result_without = temp_monthly.query(
            year=year,
            month=month,
            latitude=latitude,
            longitude=longitude,
        )
        end_without = time.perf_counter()
        without_ms = (end_without - start_without) * 1000
        
        # Test WITH pre-computed parameters (optimized query)
        start_with = time.perf_counter()
        result_with = temp_monthly.query(
            year=year,
            month=month,
            latitude=latitude,
            longitude=longitude,
            snapped_latitude=snapped_latitude,
            snapped_longitude=snapped_longitude,
            geohash=geohash,
        )
        end_with = time.perf_counter()
        with_ms = (end_with - start_with) * 1000
        
        speedup = without_ms / with_ms if with_ms > 0 else float('inf')
        time_saved = without_ms - with_ms
        percent_improvement = (time_saved / without_ms * 100) if without_ms > 0 else 0
        
        print(f"\n[PERFORMANCE] Pre-computed parameters comparison (single query):")
        print(f"  Without pre-computed params: {without_ms:.2f}ms")
        print(f"  With pre-computed params: {with_ms:.2f}ms")
        print(f"  Time saved: {time_saved:.2f}ms ({percent_improvement:.1f}% improvement)")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Both should return the same temperature
        assert result_without["temperature"] == result_with["temperature"]
        # Pre-computed version should be faster
        assert with_ms < without_ms, "Query with pre-computed params should be faster"

    def test_with_vs_without_precomputed_params_bulk_queries(self):
        """Compare performance of bulk queries with and without pre-computed parameters."""
        temp_monthly = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        # Test data (Melbourne area)
        year = 2024
        month = 1
        latitude = -37.89994
        longitude = 145.06802
        snapped_latitude = -37.900001525878906
        snapped_longitude = 145.10000610351562
        geohash = "r"
        
        num_iterations = 100
        
        # Test WITHOUT pre-computed parameters
        start_without = time.perf_counter()
        for _ in range(num_iterations):
            temp_monthly.query(
                year=year,
                month=month,
                latitude=latitude,
                longitude=longitude,
            )
        end_without = time.perf_counter()
        without_total_ms = (end_without - start_without) * 1000
        without_avg_ms = without_total_ms / num_iterations
        
        # Test WITH pre-computed parameters
        start_with = time.perf_counter()
        for _ in range(num_iterations):
            temp_monthly.query(
                year=year,
                month=month,
                latitude=latitude,
                longitude=longitude,
                snapped_latitude=snapped_latitude,
                snapped_longitude=snapped_longitude,
                geohash=geohash,
            )
        end_with = time.perf_counter()
        with_total_ms = (end_with - start_with) * 1000
        with_avg_ms = with_total_ms / num_iterations
        
        speedup = without_avg_ms / with_avg_ms if with_avg_ms > 0 else float('inf')
        time_saved_total = without_total_ms - with_total_ms
        time_saved_avg = without_avg_ms - with_avg_ms
        percent_improvement = (time_saved_total / without_total_ms * 100) if without_total_ms > 0 else 0
        
        print(f"\n[PERFORMANCE] Pre-computed parameters comparison ({num_iterations} iterations):")
        print(f"  Without pre-computed params:")
        print(f"    Total: {without_total_ms:.2f}ms")
        print(f"    Average: {without_avg_ms:.4f}ms")
        print(f"  With pre-computed params:")
        print(f"    Total: {with_total_ms:.2f}ms")
        print(f"    Average: {with_avg_ms:.4f}ms")
        print(f"  Time saved:")
        print(f"    Total: {time_saved_total:.2f}ms ({percent_improvement:.1f}% improvement)")
        print(f"    Per query: {time_saved_avg:.4f}ms")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Pre-computed version should be faster
        assert with_avg_ms < without_avg_ms, "Query with pre-computed params should be faster"

    def test_precomputed_params_overhead_breakdown(self):
        """Measure the overhead breakdown of snapping and geohash computation."""
        temp_monthly = TemperatureMonthly(
            search_radius=0.1,
            geohash_precision=1,
            max_cache_size=100,
            grid_name="01x01",
        )
        
        # Test data
        year = 2024
        month = 1
        latitude = -37.89994
        longitude = 145.06802
        snapped_latitude = -38.29999923706055
        snapped_longitude = 145.1999969482422
        geohash = "r"
        
        # Run the query once to ensure data is loaded
        temp_monthly.query(
            year=year,
            month=month,
            latitude=latitude,
            longitude=longitude,
        )
        
        # Now measure with warm cache
        num_iterations = 50
        
        # Measure WITHOUT pre-computed (includes snapping + geohash + data lookup)
        start_full = time.perf_counter()
        for _ in range(num_iterations):
            temp_monthly.query(
                year=year,
                month=month,
                latitude=latitude,
                longitude=longitude,
            )
        end_full = time.perf_counter()
        full_avg_ms = ((end_full - start_full) / num_iterations) * 1000
        
        # Measure WITH pre-computed (only data lookup)
        start_optimized = time.perf_counter()
        for _ in range(num_iterations):
            temp_monthly.query(
                year=year,
                month=month,
                latitude=latitude,
                longitude=longitude,
                snapped_latitude=snapped_latitude,
                snapped_longitude=snapped_longitude,
                geohash=geohash,
            )
        end_optimized = time.perf_counter()
        optimized_avg_ms = ((end_optimized - start_optimized) / num_iterations) * 1000
        
        # Calculate overhead
        overhead_ms = full_avg_ms - optimized_avg_ms
        overhead_percent = (overhead_ms / full_avg_ms * 100) if full_avg_ms > 0 else 0
        
        print(f"\n[PERFORMANCE] Overhead breakdown (warm cache, {num_iterations} iterations):")
        print(f"  Total query time (with snapping): {full_avg_ms:.4f}ms")
        print(f"  Pure data lookup time: {optimized_avg_ms:.4f}ms")
        print(f"  Snapping + geohash overhead: {overhead_ms:.4f}ms ({overhead_percent:.1f}%)")
        print(f"  Speedup potential: {full_avg_ms / optimized_avg_ms:.2f}x")
        
        assert overhead_ms > 0, "Snapping should add measurable overhead"
