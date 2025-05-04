class ParserStatus:
    OK_AND_WAIT = 0
    PARSING = 1
    COOKIE_EXPIRED = 2
    ETSY_API_ERROR = 3


class OrderStatus:
    Paid = "Paid"
    Canceled = "Canceled"
    Completed = "Completed"
    PartiallyRefunded = "Partially Refunded"
    FullyRefunded = "Fully Refunded"

    @classmethod
    def get_backend_status(cls, amazon_status):

        """
        PendingAvailability — Available only for pre-orders. The order has been placed, but the payment has not been authorized, and the release date of the product is in the future.

        Pending — The order has been placed, but the payment has not yet been authorized. The order is not ready for shipment.

        Unshipped — Payment is authorized, the order is ready for shipment, but no product has been shipped yet.

        PartiallyShipped — One or more items have been shipped, but not all.

        Shipped — All items in the order have been shipped.

        InvoiceUnconfirmed — All items have been shipped, but the seller has not yet confirmed to Amazon that the invoice has been sent to the buyer.

        Cancelled — The order has been cancelled.

        Unfulfillable — The order cannot be completed. This status only applies to orders completed by Amazon that have not been placed on the Amazon retail website.
        """
        mapping = {
            "Pending": cls.Paid,
            "Unshipped": cls.Paid,
            "PendingAvailability": cls.Paid,
            "PartiallyShipped": cls.Completed,
            "Shipped": cls.Completed,
            "InvoiceUnconfirmed": cls.Paid,
            "Canceled": cls.Canceled,
            "Unfulfillable": cls.Canceled
        }
        return mapping.get(amazon_status)