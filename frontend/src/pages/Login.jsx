import { useState } from "react";
import { login } from "../services/auth";
import { useNavigate } from "react-router-dom";

function Login() {
     const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const res = await login({
        email,
        password,
      });

      localStorage.setItem(
        "token",
        res.data.access_token
      );

      navigate("/dashboard");
    } catch (err) {
      alert("Invalid Credentials");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="bg-slate-900 p-8 rounded-xl w-96">
        <h1 className="text-3xl text-white mb-6 font-bold">
          VisionEdge Login
        </h1>

        <input
          className="w-full mb-4 p-3 rounded bg-slate-800 text-white"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          className="w-full mb-4 p-3 rounded bg-slate-800 text-white"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 hover:bg-blue-700 p-3 rounded text-white"
        >
          Login
        </button>
      </div>
    </div>
  );
}

export default Login;