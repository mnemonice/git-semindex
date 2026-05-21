use criterion::{criterion_group, criterion_main, Criterion};

// A simple baseline benchmark to establish performance profiling.
// This ensures that `criterion` is properly integrated.
fn benchmark_noop(c: &mut Criterion) {
    c.bench_function("noop", |b| {
        b.iter(|| {
            let _ = 1 + 1;
        })
    });
}

criterion_group!(benches, benchmark_noop);
criterion_main!(benches);
