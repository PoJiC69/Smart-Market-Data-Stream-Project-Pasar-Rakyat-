import React from "react";

/**
 * Simple ErrorBoundary - shows error message and stack so we can see why app blank.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // store component stack
    this.setState({ error, info });
    // also log to console
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: "Inter, Arial, sans-serif", color: "#111" }}>
          <h2 style={{ color: "#b91c1c" }}>Aplikasi mengalami error saat runtime</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#fff4f4", padding: 12, borderRadius: 8 }}>
            {String(this.state.error && this.state.error.toString())}
            {"\n\n"}
            {this.state.info && this.state.info.componentStack}
          </pre>
          <p style={{ color: "#555" }}>
            Copy error message diatas dan kirim ke saya agar saya bisa bantu perbaiki. Sementara itu reload halaman untuk mencoba lagi.
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}