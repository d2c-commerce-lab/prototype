import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signup } from "../../services/authApi";
import { getStoredUser, setStoredUser } from "../../stores/userStore";

type SignupFormState = {
  email: string;
  password: string;
  user_name: string;
  marketing_opt_in_yn: boolean;
};

const initialFormState: SignupFormState = {
  email: "",
  password: "",
  user_name: "",
  marketing_opt_in_yn: true,
};

function validateSignupForm(form: SignupFormState) {
  if (!form.user_name.trim()) {
    return "이름을 입력해주세요.";
  }

  if (!form.email.trim()) {
    return "이메일을 입력해주세요.";
  }

  if (!form.email.includes("@")) {
    return "올바른 이메일 형식으로 입력해주세요.";
  }

  if (!form.password.trim()) {
    return "비밀번호를 입력해주세요.";
  }

  if (form.password.length < 8) {
    return "비밀번호는 8자 이상 입력해주세요.";
  }

  return null;
}

export function SignupPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState<SignupFormState>(initialFormState);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  useEffect(() => {
    const storedUser = getStoredUser();

    if (storedUser) {
      navigate("/products", { replace: true });
    }
  }, [navigate]);

  const handleInputChange = (field: keyof SignupFormState, value: string | boolean) => {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const validationMessage = validateSignupForm(form);

    if (validationMessage) {
      setErrorMessage(validationMessage);
      setSuccessMessage(null);
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);
      setSuccessMessage(null);

      const createdUser = await signup({
        email: form.email.trim(),
        password: form.password,
        user_name: form.user_name.trim(),
        marketing_opt_in_yn: form.marketing_opt_in_yn,
      });

      setStoredUser(createdUser);
      setSuccessMessage("회원가입이 완료되었습니다. 상품 목록으로 이동합니다.");

      setTimeout(() => {
        navigate("/products");
      }, 600);
    } catch {
      setErrorMessage("회원가입에 실패했습니다. 입력 정보를 확인한 뒤 다시 시도해주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <p className="section-eyebrow">Create Account</p>
          <h1>회원가입</h1>
          <p>
            D2C Commerce Prototype의 상품 탐색, 장바구니, 주문, 리뷰 흐름을
            검증하기 위한 사용자 계정을 생성합니다.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>이름</span>
            <input
              type="text"
              value={form.user_name}
              placeholder="홍길동"
              onChange={(event) => handleInputChange("user_name", event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>이메일</span>
            <input
              type="email"
              value={form.email}
              placeholder="user@example.com"
              onChange={(event) => handleInputChange("email", event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>비밀번호</span>
            <input
              type="password"
              value={form.password}
              placeholder="8자 이상 입력"
              onChange={(event) => handleInputChange("password", event.target.value)}
            />
          </label>

          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={form.marketing_opt_in_yn}
              onChange={(event) =>
                handleInputChange("marketing_opt_in_yn", event.target.checked)
              }
            />
            <span>마케팅 정보 수신에 동의합니다.</span>
          </label>

          {errorMessage && <div className="state-box error">{errorMessage}</div>}
          {successMessage && <div className="state-box success">{successMessage}</div>}

          <button type="submit" className="primary-button auth-submit-button" disabled={isSubmitting}>
            {isSubmitting ? "가입 처리 중..." : "회원가입"}
          </button>
        </form>

        <div className="auth-footer">
          <span>이미 계정이 있으신가요?</span>
          <Link to="/login">로그인</Link>
        </div>
      </div>
    </section>
  );
}