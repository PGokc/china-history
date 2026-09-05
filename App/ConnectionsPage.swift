import SwiftUI

struct RelatedPeople: View {
    let store: HistoryStore
    let personID: String
    var limit: Int? = nil
    var otherIDs: [String] {
        store.associates(personID).reduce(into: [String]()) { ids, link in
            let id = link.from == personID ? link.to : link.from
            if !ids.contains(id) { ids.append(id) }
        }
    }
    var visibleIDs: [String] { limit.map { Array(otherIDs.prefix($0)) } ?? otherIDs }
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            sectionTitle("同处一个时代")
            ForEach(visibleIDs, id: \.self) { id in
                let other = store.person(id)
                NavigationLink(value: DetailRoute.person(other.id)) {
                    HStack(alignment: .top, spacing: 16) {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(other.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                            ForEach(store.associates(personID).filter { $0.from == id || $0.to == id }) { link in
                                Text(link.period).font(.caption.monospacedDigit()).foregroundStyle(Theme.cinnabar)
                                Text(link.from == personID ? link.role : link.inverse).font(.caption).foregroundStyle(Theme.muted)
                            }
                        }.frame(maxWidth: .infinity, alignment: .leading)
                    }.frame(minHeight: 52).padding(.vertical, 9).contentShape(Rectangle())
                }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("associate_\(other.id)")
                Rectangle().fill(Theme.line.opacity(0.42)).frame(height: 0.5)
            }
            if let limit, otherIDs.count > limit {
                NavigationLink("全部相关人物", value: DetailRoute.connections(personID)).font(.subheadline).frame(minHeight: 48).accessibilityIdentifier("allAssociates")
            }
        }
    }
}
struct ConnectionsPage: View {
    let store: HistoryStore
    let personID: String
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 26) {
                RelatedPeople(store: store, personID: personID)
                DisclosureGroup("关系与出处") {
                    ForEach(store.associates(personID)) { link in
                        VStack(alignment: .leading, spacing: 10) { Text("\(store.person(link.from).name)与\(store.person(link.to).name)").font(.headline); Text(link.note).font(.subheadline); SourcesView(store: store, ids: link.sources, compact: true) }.padding(.vertical, 14)
                    }
                }
            }.padding(24)
        }.background(Theme.paper).foregroundStyle(Theme.text).navigationTitle(store.person(personID).name).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
}
