function App() {
  return (
    <div className="flex h-screen items-center justify-center bg-df-bg-primary">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-df-text-primary">DataFlow</h1>
        <p className="mt-2 text-df-text-secondary">
          Data science notebook environment
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <span className="inline-block h-3 w-3 rounded-full bg-df-state-idle" />
          <span className="inline-block h-3 w-3 rounded-full bg-df-state-running" />
          <span className="inline-block h-3 w-3 rounded-full bg-df-state-success" />
          <span className="inline-block h-3 w-3 rounded-full bg-df-state-error" />
          <span className="inline-block h-3 w-3 rounded-full bg-df-state-stale" />
        </div>
      </div>
    </div>
  );
}

export default App;
