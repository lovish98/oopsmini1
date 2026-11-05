"""OOP-only movie ticket booking demo (in-memory, no database required)."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Movie:
    title: str
    genre: str
    duration_minutes: int


@dataclass
class Seat:
    number: str
    premium: bool = False
    reserved: bool = False

    def reserve(self) -> None:
        if self.reserved:
            raise ValueError(f"Seat {self.number} is already reserved.")
        self.reserved = True

    def release(self) -> None:
        self.reserved = False


@dataclass
class Show:
    show_id: int
    movie: Movie
    theater: str
    starts_at: str
    base_price: float
    seats: dict[str, Seat] = field(default_factory=dict)

    def available_seats(self) -> list[str]:
        return sorted(number for number, seat in self.seats.items() if not seat.reserved)

    def price_for(self, seat: Seat) -> float:
        return self.base_price * (1.5 if seat.premium else 1.0)


@dataclass
class Customer:
    name: str
    email: str


@dataclass
class Payment:
    amount: float
    method: str
    status: str = "PAID"

    def refund(self) -> None:
        self.status = "REFUNDED"


@dataclass
class Booking:
    booking_id: int
    customer: Customer
    show: Show
    seats: list[Seat]
    payment: Payment
    booked_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="minutes"))
    status: str = "CONFIRMED"

    @property
    def total(self) -> float:
        return sum(self.show.price_for(seat) for seat in self.seats)

    def cancel(self) -> None:
        if self.status != "CONFIRMED":
            raise ValueError("This booking is already cancelled.")
        for seat in self.seats:
            seat.release()
        self.payment.refund()
        self.status = "CANCELLED"


class BookingSystem:
    """Coordinates objects and keeps application data in memory."""
    def __init__(self) -> None:
        movie = Movie("The Grand Adventure", "Adventure", 128)
        seats = {}
        for row in range(1, 6):
            for letter in "ABCDE":
                number = f"{letter}{row}"
                seats[number] = Seat(number, premium=(row >= 4))
        self.shows = {
            1: Show(1, movie, "Starlight Cinemas, Screen 1", "2026-12-01 18:30", 250.0, seats),
            2: Show(2, movie, "Starlight Cinemas, Screen 1", "2026-12-01 21:30", 250.0,
                    {number: Seat(number, premium=(int(number[1:]) >= 4)) for number in seats}),
        }
        self.bookings: list[Booking] = []
        self.next_booking_id = 1

    def book(self, customer: Customer, show_id: int, seat_numbers: list[str], method: str) -> Booking:
        if show_id not in self.shows:
            raise ValueError("Show does not exist.")
        if method.upper() not in {"CARD", "UPI", "CASH"}:
            raise ValueError("Use CARD, UPI, or CASH as payment method.")
        show = self.shows[show_id]
        numbers = list(dict.fromkeys(n.strip().upper() for n in seat_numbers if n.strip()))
        if not numbers:
            raise ValueError("Choose at least one seat.")
        if any(number not in show.seats for number in numbers):
            raise ValueError("One or more seat numbers are invalid.")
        selected = [show.seats[number] for number in numbers]
        if any(seat.reserved for seat in selected):
            raise ValueError("One or more seats have already been booked.")
        for seat in selected:
            seat.reserve()
        total = sum(show.price_for(seat) for seat in selected)
        booking = Booking(self.next_booking_id, customer, show, selected, Payment(total, method.upper()))
        self.bookings.append(booking)
        self.next_booking_id += 1
        return booking

    def cancel(self, booking_id: int) -> None:
        booking = next((item for item in self.bookings if item.booking_id == booking_id), None)
        if booking is None:
            raise ValueError("Booking not found.")
        booking.cancel()


def main() -> None:
    system = BookingSystem()
    while True:
        print("\n=== OOP MOVIE TICKET BOOKING ===")
        print("1. Browse shows\n2. Book tickets\n3. View bookings\n4. Cancel booking\n0. Exit")
        choice = input("Select: ").strip()
        try:
            if choice == "1":
                for show in system.shows.values():
                    print(f"Show {show.show_id}: {show.movie.title} ({show.movie.genre}, {show.movie.duration_minutes} min) | {show.starts_at} | {show.theater} | ₹{show.base_price:.2f} base")
            elif choice == "2":
                for show in system.shows.values():
                    print(f"Show {show.show_id}: {show.movie.title} — {show.starts_at} — {show.theater}")
                show_id = int(input("Show ID: "))
                print("Available seats:", ", ".join(system.shows[show_id].available_seats()))
                numbers = input("Seats (comma separated): ").split(",")
                customer = Customer(input("Name: ").strip(), input("Email: ").strip())
                if not customer.name or not customer.email:
                    raise ValueError("Name and email are required.")
                method = input("Payment method (CARD/UPI/CASH): ").strip()
                booking = system.book(customer, show_id, numbers, method)
                print(f"Confirmed booking #{booking.booking_id}; seats {', '.join(s.number for s in booking.seats)}; total ₹{booking.total:.2f}")
            elif choice == "3":
                if not system.bookings:
                    print("No bookings yet.")
                for booking in system.bookings:
                    seats = ", ".join(seat.number for seat in booking.seats)
                    print(f"#{booking.booking_id} | {booking.customer.name} | {booking.show.movie.title} | {booking.show.starts_at} | {seats} | ₹{booking.total:.2f} | {booking.status} | {booking.payment.status}")
            elif choice == "4":
                system.cancel(int(input("Booking ID to cancel: ")))
                print("Booking cancelled; seats released and payment refunded.")
            elif choice == "0":
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, KeyError) as exc:
            print(f"Could not complete request: {exc}")


if __name__ == "__main__":
    main()
