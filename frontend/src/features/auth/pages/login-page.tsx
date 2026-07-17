import { Link } from "react-router-dom";

import { ROUTES } from "@/config/routes/route-paths";

export default function LoginPage() {
	return (
		<div>
			<h2 className="text-lg font-semibold text-text-primary">Sign In</h2>
			<p className="mt-1 text-sm text-text-secondary">
				Login page coming soon.
			</p>
			<p className="mt-4 text-sm text-text-secondary">
				Don&apos;t have an account?{" "}
				<Link
					to={ROUTES.REGISTER_BUSINESS}
					className="font-medium text-primary hover:underline"
				>
					Create one
				</Link>
			</p>
		</div>
	);
}
