import { useEffect, useMemo, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { Store } from "lucide-react";

import { ROUTES } from "@/config/routes/route-paths";

type Language = "en" | "fr" | "sw";

const LANGUAGE_STORAGE_KEY = "elaho.language";

function getInitialLanguage(): Language {
	if (typeof window === "undefined") {
		return "en";
	}

	const saved = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
	if (saved === "fr" || saved === "sw") {
		return saved;
	}

	return "en";
}

function getIsAuthenticated(): boolean {
	if (typeof window === "undefined") {
		return false;
	}

	// Temporary guard until auth context/store is wired.
	return Boolean(
		window.localStorage.getItem("access_token") ||
			window.localStorage.getItem("tokens")
	);
}

export default function AuthLayout() {
	const [language, setLanguage] = useState<Language>(getInitialLanguage);

	const isAuthenticated = useMemo(() => getIsAuthenticated(), []);

	useEffect(() => {
		document.documentElement.lang = language;
		document.documentElement.dir = "ltr";
		window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
	}, [language]);

	if (isAuthenticated) {
		return <Navigate to={ROUTES.DASHBOARD} replace />;
	}

	return (
		<main className="relative min-h-screen overflow-hidden bg-[linear-gradient(180deg,#d7e9f2_0%,#eeece3_58%,#f3ede2_100%)] px-4 py-5 sm:px-6 md:py-10">
			<div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_top,_rgba(16,119,145,0.2),_transparent_70%)]" />

			<section className="relative mx-auto w-full max-w-[34rem] md:max-w-5xl">
				<div className="md:grid md:grid-cols-[minmax(0,480px)_minmax(0,1fr)] md:items-end md:gap-8">
					<div className="rounded-[30px] border border-slate-200/80 bg-[#f7fafc] p-5 shadow-[0_28px_45px_rgba(15,23,42,0.15)] sm:p-8">
						<div className="mb-10 flex justify-end">
							<div
								className="inline-flex rounded-full border border-slate-300 bg-slate-50 p-1"
								role="group"
								aria-label="Language switcher"
							>
								<button
									type="button"
									onClick={() => setLanguage("en")}
									className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
										language === "en"
											? "bg-slate-900 text-white"
											: "text-slate-600 hover:text-slate-900"
									}`}
									aria-pressed={language === "en"}
								>
									EN
								</button>
								<button
									type="button"
									onClick={() => setLanguage("fr")}
									className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
										language === "fr"
											? "bg-slate-900 text-white"
											: "text-slate-600 hover:text-slate-900"
									}`}
									aria-pressed={language === "fr"}
								>
									FR
								</button>
								<button
									type="button"
									onClick={() => setLanguage("sw")}
									className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
										language === "sw"
											? "bg-slate-900 text-white"
											: "text-slate-600 hover:text-slate-900"
									}`}
									aria-pressed={language === "sw"}
								>
									SW
								</button>
							</div>
						</div>

						<div className="mb-8 text-center">
							<div className="mx-auto mb-7 inline-flex h-[68px] w-[68px] items-center justify-center rounded-3xl bg-gradient-to-b from-cyan-700 to-cyan-800 text-white shadow-lg shadow-cyan-900/20">
								<Store size={30} strokeWidth={2.2} aria-hidden="true" />
							</div>
							<p className="text-[1.95rem] font-bold leading-none tracking-[0.18em] text-cyan-900">
								ELAHO POS
							</p>
							<h1 className="mt-5 text-[3.45rem] font-black leading-[0.98] tracking-tight text-slate-900">
								Welcome Back
							</h1>
							<p className="mx-auto mt-4 max-w-[19.5rem] text-[1.35rem] leading-[1.35] text-slate-600 sm:text-[1.45rem]">
								Manage your store with confidence and precision.
							</p>
						</div>

						<div className="space-y-4">
							<Outlet />
						</div>
					</div>

					<div className="mt-6 space-y-6 md:mt-0">
						<article className="overflow-hidden rounded-3xl shadow-[0_16px_32px_rgba(15,23,42,0.2)]">
							<div className="relative h-[220px] bg-[linear-gradient(130deg,#8db9cc_0%,#4f6673_45%,#25313a_100%)] md:h-[220px]">
								<div className="absolute inset-0 bg-black/25" />
								<div className="absolute inset-x-6 bottom-5 text-white">
									<p className="text-xs font-semibold tracking-[0.16em] text-cyan-100">
										NEW FEATURE
									</p>
									<p className="mt-2 text-2xl font-bold leading-tight">
										Predictive Inventory Management
									</p>
								</div>
							</div>
						</article>

						<footer className="pb-4 pt-1 text-center text-slate-500">
							<nav className="flex items-center justify-center gap-8 text-[1.45rem] leading-none sm:text-[1.6rem]">
								<a href="#" className="transition hover:text-slate-700">
									Security
								</a>
								<a href="#" className="transition hover:text-slate-700">
									Privacy
								</a>
								<a href="#" className="transition hover:text-slate-700">
									Help
								</a>
							</nav>
							<p className="mt-4 text-[1.45rem] leading-none sm:text-[1.6rem]">© 2026 Elaho POS Systems</p>
						</footer>
					</div>
				</div>
			</section>
		</main>
	);
}
