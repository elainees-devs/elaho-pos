import { Navigate, RouteObject } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import AuthLayout from "@/features/auth/layouts/auth-layout";
import LoginPagePlaceholder from "@/features/auth/pages/login-page";
import RegisterBusinessPage from "@/features/auth/pages/register-business-page";
import RegisterUserPage from "@/features/auth/pages/register-user-page";

const AUTH_BASE_PATH = "/auth";

const childPath = (path: string) => path.replace(/^\/auth\//, "").replace(/^\//, "");

const ForgotPasswordPagePlaceholder = () => (
	<div>Forgot Password Page - TODO</div>
);
const ResetPasswordPagePlaceholder = () => (
	<div>Reset Password Page - TODO</div>
);
const VerifyEmailPagePlaceholder = () => (
	<div>Verify Email Page - TODO</div>
);

export const authRoutes: RouteObject[] = [
	{
		path: AUTH_BASE_PATH,
		element: <AuthLayout />,
		children: [
			{
				index: true,
				element: (
					<Navigate
						to={ROUTES.LOGIN}
						replace
					/>
				),
			},
			{
				path: childPath(ROUTES.LOGIN),
				element: <LoginPagePlaceholder />,
			},
			{
				path: childPath(ROUTES.REGISTER),
				element: <RegisterUserPage />,
			},
			{
				path: childPath(ROUTES.REGISTER_BUSINESS),
				element: <RegisterBusinessPage />,
			},
			{
				path: childPath(ROUTES.FORGOT_PASSWORD),
				element: <ForgotPasswordPagePlaceholder />,
			},
			{
				path: childPath(ROUTES.RESET_PASSWORD),
				element: <ResetPasswordPagePlaceholder />,
			},
			{
				path: childPath(ROUTES.VERIFY_EMAIL),
				element: <VerifyEmailPagePlaceholder />,
			},
			{
				path: "*",
				element: (
					<Navigate
						to={ROUTES.LOGIN}
						replace
					/>
				),
			},
		],
	},
];
