import SwiftUI

struct RelatedPeople: View {
    let store: HistoryStore
    let personID: String
    var limit: Int? = nil
    var title = "同处一个时代"
    var includeFamily = false
    private var associatedIDs: [String] {
        store.associates(personID).reduce(into: [String]()) { ids, link in
            let id = link.from == personID ? link.to : link.from
            if !ids.contains(id) { ids.append(id) }
        }
    }
    var otherIDs: [String] {
        guard includeFamily else { return associatedIDs }
        let family = store.parents(personID).map(\.to)
            + store.spouses(personID).map(\.id)
            + store.children(personID).map(\.id)
        return (associatedIDs + family).reduce(into: [String]()) { ids, id in
            if id != personID && !ids.contains(id) { ids.append(id) }
        }
    }
    var visibleIDs: [String] { limit.map { Array(otherIDs.prefix($0)) } ?? otherIDs }
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            sectionTitle(title)
            ForEach(visibleIDs, id: \.self) { id in
                let other = store.person(id)
                NavigationLink(value: DetailRoute.person(other.id)) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text(other.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                        Text(relationLine(for: id))
                            .font(.caption).foregroundStyle(Theme.muted).lineLimit(2)
                    }
                    .frame(maxWidth: .infinity, minHeight: 50, alignment: .leading)
                    .padding(.vertical, 8).contentShape(Rectangle())
                }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("associate_\(other.id)")
                Rectangle().fill(Theme.line.opacity(0.42)).frame(height: 0.5)
            }
            if let limit, otherIDs.count > limit {
                NavigationLink(value: DetailRoute.connections(personID)) {
                    Text("查看全部相关人物")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(Theme.cinnabar)
                        .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                        .contentShape(Rectangle())
                }
                .buttonStyle(QuietRowStyle())
                .accessibilityIdentifier("allAssociates")
            }
        }
    }
    private func relationLine(for id: String) -> String {
        if let link = store.associates(personID).first(where: {
            ($0.from == personID && $0.to == id) || ($0.to == personID && $0.from == id)
        }) {
            let role = link.from == personID ? link.role : link.inverse
            return [link.period, role].filter { !$0.isEmpty }.joined(separator: "　")
        }
        if let parent = store.parents(personID).first(where: { $0.to == id }) {
            return "\(store.parentLabel(parent.kind))　\(store.person(id).call)"
        }
        if store.spouses(personID).contains(where: { $0.id == id }) {
            return "配偶　\(store.person(id).call)"
        }
        if let child = store.children(personID).first(where: { $0.id == id }) {
            return "\(store.orderLabel(child))　\(child.call)"
        }
        return store.person(id).call
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
