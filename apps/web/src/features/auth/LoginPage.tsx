import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../../services/authApi";
import { getStoredUser, setStoredUser } from "../../stores/userStore";

type LoginFormState = {
  email: string;
  password: string;
};

const initialFormState: LoginFormState = {
  email: "",
  password: "",
};

function validateLoginForm(form: LoginFormState) {
  if (!form.email.trim()) {
    return "이메일을 입력해주세요.";
  }

  if (!form.email.includes("@")) {
    return "올바른 이메일 형식으로 입력해주세요.";
  }

  if (!form.password.trim()) {
    return "비밀번호를 입력해주세요.";
  }

  return null;
}

export function LoginPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<LoginFormState>(initialFormState);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const storedUser = getStoredUser();

    if (storedUser) {
      navigate("/products", { replace: true });
    }
  }, [navigate]);

  const handleInputChange = (field: keyof LoginFormState, value: string) => {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationMessage = validateLoginForm(form);

    if (validationMessage) {
      setErrorMessage(validationMessage);
      setSuccessMessage(null);
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      setSuccessMessage(null);

      const loggedInUser = await login({
        email: form.email.trim(),
        password: form.password,
      });

      setStoredUser(loggedInUser);
      setSuccessMessage("로그인이 완료되었습니다. 상품 목록으로 이동합니다.");

      setTimeout(() => {
        navigate("/products");
      }, 600);
    } catch {
      setErrorMessage("로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <p className="section-eyebrow">Sign In</p>
          <h1>로그인</h1>
          <p>
            기존 계정으로 로그인하여 장바구니, 주문, 리뷰 흐름을 이어서 검증합니다.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>이메일</span>
            <input
              type="email"
              value={form.email}
              placeholder="user@example.com"
              autoComplete="email"
              onChange={(event) => handleInputChange("email", event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>비밀번호</span>
            <input
              type="password"
              value={form.password}
              placeholder="비밀번호 입력"
              autoComplete="current-password"
              onChange={(event) => handleInputChange("password", event.target.value)}
            />
          </label>

          {errorMessage && <div className="state-box error">{errorMessage}</div>}
          {successMessage && <div className="state-box success">{successMessage}</div>}

          <button
            type="submit"
            className="primary-button auth-submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? "로그인 처리 중..." : "로그인"}
          </button>
        </form>

        <div className="auth-footer">
          <span>아직 계정이 없으신가요?</span>
          <Link to="/signup">회원가입</Link>
        </div>
      </div>
    </section>
  );
}