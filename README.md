# Movie Ticket Booking — OOP Project

Standalone Python console app focused on Object-Oriented Programming. All information is held in memory and resets when the program exits.

## Run

```bash
python3 main.py
```

## OOP concepts shown

- **Classes and objects:** `Movie`, `Seat`, `Show`, `Customer`, `Payment`, and `Booking` model the system.
- **Encapsulation:** seat reservation and release are performed by `Seat`; payment refunds by `Payment`; cancellation by `Booking`.
- **Abstraction:** `BookingSystem.book()` coordinates seat validation, price calculation, and booking creation.
- **Composition:** a `Show` has seats and a movie; a `Booking` has a customer, show, seats, and payment.
- **Properties:** `Booking.total` calculates the ticket price from the selected seats.

Premium seats are priced at 1.5 times the base price. The sample has two shows on December 1, 2026.

## Files

- `main.py` — complete in-memory console application.
