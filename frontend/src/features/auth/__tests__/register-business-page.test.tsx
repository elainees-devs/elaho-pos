import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import RegisterBusinessPage from "../pages/register-business-page";

vi.mock("@/features/business/services/business.service", () => ({
	businessService: {
		register: vi.fn(),
	},
}));

import { businessService } from "@/features/business/services/business.service";

function renderPage() {
	return render(
		<MemoryRouter initialEntries={["/auth/register-business"]}>
			<RegisterBusinessPage />
		</MemoryRouter>
	);
}

describe("RegisterBusinessPage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renders the registration form", () => {
		renderPage();
		expect(screen.getByText("Set up your business")).toBeInTheDocument();
		expect(screen.getByLabelText(/business name/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/kra pin/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /create account/i })).toBeInTheDocument();
	});

	it("shows sign-in link pointing to /auth/login", () => {
		renderPage();
		const signInLink = screen.getByRole("link", { name: /sign in/i });
		expect(signInLink).toHaveAttribute("href", "/auth/login");
	});

	it("shows validation errors for required fields", async () => {
		const user = userEvent.setup();
		renderPage();

		await user.click(screen.getByRole("button", { name: /create account/i }));

		expect(screen.getByText("Business name must be at least 2 characters")).toBeInTheDocument();
		expect(screen.getByText("KRA PIN is required")).toBeInTheDocument();
		expect(screen.getByText("First name must be at least 2 characters")).toBeInTheDocument();
		expect(screen.getByText("Last name must be at least 2 characters")).toBeInTheDocument();
		expect(screen.getByText("Invalid email address")).toBeInTheDocument();
	});

	it("shows password mismatch error", async () => {
		const user = userEvent.setup();
		renderPage();

		await user.type(screen.getByLabelText(/business name/i), "Acme Ltd");
		await user.type(screen.getByLabelText(/kra pin/i), "A001234567B");
		await user.type(screen.getByLabelText(/first name/i), "Jane");
		await user.type(screen.getByLabelText(/last name/i), "Doe");
		await user.type(screen.getByLabelText(/^email$/i), "jane@acme.co.ke");
		await user.type(screen.getByLabelText(/^password$/i), "Password1");
		await user.type(screen.getByLabelText(/confirm password/i), "Password2");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		expect(screen.getByText("Passwords do not match")).toBeInTheDocument();
	});

	it("shows validation error for invalid email", async () => {
		const user = userEvent.setup();
		renderPage();

		await user.type(screen.getByLabelText(/^email$/i), "notanemail");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		expect(screen.getByText("Invalid email address")).toBeInTheDocument();
	});

	it("submits valid data and shows success message", async () => {
		const user = userEvent.setup();
		(businessService.register as ReturnType<typeof vi.fn>).mockResolvedValueOnce({});

		renderPage();

		await user.type(screen.getByLabelText(/business name/i), "Acme Ltd");
		await user.type(screen.getByLabelText(/kra pin/i), "A001234567B");
		await user.type(screen.getByLabelText(/first name/i), "Jane");
		await user.type(screen.getByLabelText(/last name/i), "Doe");
		await user.type(screen.getByLabelText(/^email$/i), "jane@acme.co.ke");
		await user.type(screen.getByLabelText(/^password$/i), "Password1");
		await user.type(screen.getByLabelText(/confirm password/i), "Password1");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText("Business registered successfully!")).toBeInTheDocument();
		});

		expect(businessService.register).toHaveBeenCalledWith(
			expect.objectContaining({
				business_name: "Acme Ltd",
				kra_pin: "A001234567B",
				first_name: "Jane",
				last_name: "Doe",
				email: "jane@acme.co.ke",
				password: "Password1",
			})
		);
	});

	it("shows error message on API failure", async () => {
		const user = userEvent.setup();
		(businessService.register as ReturnType<typeof vi.fn>).mockRejectedValueOnce({
			response: { data: { detail: "A business with this email already exists." } },
		});

		renderPage();

		await user.type(screen.getByLabelText(/business name/i), "Acme Ltd");
		await user.type(screen.getByLabelText(/kra pin/i), "A001234567B");
		await user.type(screen.getByLabelText(/first name/i), "Jane");
		await user.type(screen.getByLabelText(/last name/i), "Doe");
		await user.type(screen.getByLabelText(/^email$/i), "jane@acme.co.ke");
		await user.type(screen.getByLabelText(/^password$/i), "Password1");
		await user.type(screen.getByLabelText(/confirm password/i), "Password1");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText("A business with this email already exists.")).toBeInTheDocument();
		});
	});

	it("shows generic error on network failure", async () => {
		const user = userEvent.setup();
		(businessService.register as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error("Network Error"));

		renderPage();

		await user.type(screen.getByLabelText(/business name/i), "Acme Ltd");
		await user.type(screen.getByLabelText(/kra pin/i), "A001234567B");
		await user.type(screen.getByLabelText(/first name/i), "Jane");
		await user.type(screen.getByLabelText(/last name/i), "Doe");
		await user.type(screen.getByLabelText(/^email$/i), "jane@acme.co.ke");
		await user.type(screen.getByLabelText(/^password$/i), "Password1");
		await user.type(screen.getByLabelText(/confirm password/i), "Password1");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		await waitFor(() => {
			expect(screen.getByText("Something went wrong. Please try again.")).toBeInTheDocument();
		});
	});

	it("disables submit button while submitting", async () => {
		const user = userEvent.setup();
		(businessService.register as ReturnType<typeof vi.fn>).mockImplementation(
			() => new Promise((resolve) => setTimeout(resolve, 1000))
		);

		renderPage();

		await user.type(screen.getByLabelText(/business name/i), "Acme Ltd");
		await user.type(screen.getByLabelText(/kra pin/i), "A001234567B");
		await user.type(screen.getByLabelText(/first name/i), "Jane");
		await user.type(screen.getByLabelText(/last name/i), "Doe");
		await user.type(screen.getByLabelText(/^email$/i), "jane@acme.co.ke");
		await user.type(screen.getByLabelText(/^password$/i), "Password1");
		await user.type(screen.getByLabelText(/confirm password/i), "Password1");

		await user.click(screen.getByRole("button", { name: /create account/i }));

		expect(screen.getByRole("button", { name: /creating account/i })).toBeDisabled();
	});
});
