export type SignupRequest = {
    email: string;
    password: string;
    user_name: string;
    marketing_opt_in_yn: boolean;
};

export type AuthUser = {
    user_id: string;
    email: string;
    user_name: string;
    user_status: string;
    marketing_opt_in_yn?: boolean;
};