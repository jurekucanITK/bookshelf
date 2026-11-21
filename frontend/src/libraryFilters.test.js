import { expect, it } from "vitest";
import { applyFilters } from "./libraryFilters.js";

function book(id, { title, author = "Brandon Sanderson", series = null, seriesNumber = null,
    format = "print", readingStatus = null } = {}) {
    return {
        id,
        reading_status: readingStatus,
        edition: {
            title: null,
            format,
            publisher_collection: null,
            work: { title, author, genre: null, series, series_number: seriesNumber },
        },
    };
}

const ids = (items) => items.map((item) => item.id);

it("applyFilters filtrira po formatu ter po seriji in prebranem", () => {
    const items = [
        book(1, { title: "The Final Empire", series: "Mistborn", readingStatus: "read" }),
        book(2, { title: "The Well of Ascension", series: "Mistborn", format: "ebook" }),
        book(3, { title: "The Hero of Ages", series: "Mistborn", readingStatus: "reading" }),
        book(4, { title: "Elantris", format: "ebook" }),
    ];

    expect(ids(applyFilters(items, new URLSearchParams("format=ebook")))).toEqual([2, 4]);
    expect(ids(applyFilters(items, new URLSearchParams("series=Mistborn&read=read")))).toEqual([1]);
    expect(ids(applyFilters(items, new URLSearchParams("series=Mistborn&read=unread")))).toEqual([
        2, 3,
    ]);
});

it("applyFilters razvrsti po priimku avtorja, nato po vrsti v seriji", () => {
    const items = [
        book(1, { title: "The Hero of Ages", series: "Mistborn", seriesNumber: 3 }),
        book(2, { title: "The Blade Itself", author: "Joe Abercrombie" }),
        book(3, { title: "The Final Empire", series: "Mistborn", seriesNumber: 1 }),
        book(4, { title: "The Well of Ascension", series: "Mistborn", seriesNumber: 2 }),
    ];

    expect(ids(applyFilters(items, new URLSearchParams("sort=author")))).toEqual([2, 3, 4, 1]);
    expect(ids(applyFilters(items, new URLSearchParams("sort=-author")))).toEqual([3, 4, 1, 2]);
});
