import Foundation

@main struct ReaderLogicTests {
    static func main() {
        precondition(EventChronology.year("18世纪中后期") == nil)
        precondition(EventChronology.year("永乐初") == nil)
        precondition(EventChronology.year("1750年以后") == 1750)
        precondition(EventChronology.year("742—744年") == 742)
        precondition(EventChronology.year("17世纪中后期", placement: 1650) == 1650)
        precondition(EventChronology.precedes("1650年", placement: nil, id: "a", "17世纪后期", placement: 1670, id: "b"))
        precondition(EventChronology.precedes("1403年", placement: nil, id: "a", "永乐初", placement: 1403, id: "b"))
        precondition(!EventChronology.precedes("未详", placement: nil, id: "a", "1403年", placement: nil, id: "b"))
        let order = ["first", "second", "third"]
        precondition(ReadingProgress.section(positions: ["first": -650, "second": 90, "third": 900], order: order) == "first")
        precondition(ReadingProgress.section(positions: ["first": -650, "second": 25, "third": 900], order: order) == "second")
        precondition(ReadingProgress.section(positions: ["first": 300, "second": 900], order: order) == nil)
        precondition(ReadingProgress.section(positions: ["first": -2000, "second": -900, "third": -100], order: order) == "third")
        precondition(ReadingProgress.section(positions: [:], order: order) == nil)
        print("PASS: 13 chronology and reading-position regression cases")
    }
}
