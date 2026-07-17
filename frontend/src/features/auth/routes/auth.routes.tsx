import { Navigate, RouteObject } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";
import AuthLayout from "@/features/auth/layouts/auth-layout";
import RegisterBusinessPage from "@/features/auth/pages/register-business-page";
import RegisterUserPage from "@/features/auth/pages/register-user-page";

const AUTH_BASE_PATH = "/auth";

const childPath = (path: string) => path.replace(/^\//, "");

// TODO(auth): Replace these placeholders with the actual page components
// once they are implemented.
const LoginPagePlaceholder = () => <div>Login Page - TODO</div>;
const ForgotPasswordPagePlaceholder = () => (
	<div>Forgot Password Page - TODO</div>
);
const ResetPasswordPagePlaceholder = () => (
	<div>Reset Password Page - TODO</div>
);
const VerifyEmailPagePlaceholder = () => (
	<div>Verify Email Page - TODO</div>
);
const VerificationSentPagePlaceholder = () => (
	<div>Email Verification Sent Page - TODO</div>
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
						to={childPath(ROUTES.LOGIN)}
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
				path: childPath(ROUTES.VERIFY_EMAIL),
				element: <VerificationSentPagePlaceholder />,
			},
			{
				path: "*",
				element: (
					<Navigate
						to={childPath(ROUTES.LOGIN)}
						replace
					/>
				),
			},
		],
	},
];