import SwiftUI

struct GlobalSearchLink: View {
    var body: some View {
        NavigationLink(value: DetailRoute.search) {
            Image(systemName: "magnifyingglass")
        }
        .accessibilityLabel("全局检索")
        .accessibilityIdentifier("globalSearch")
    }
}

struct GlobalSearchPage: View {
    let store: HistoryStore
    @State private var query = ""

    private var term: String {
        query.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func includes(_ values: [String]) -> Bool {
        !term.isEmpty && values.contains { $0.localizedStandardContains(term) }
    }

    private func personText(_ person: Person) -> [String] {
        var values = [person.name, person.call, person.temple, person.era, person.reign, person.summary, person.kind, person.note]
        if let article = store.article(person.id) {
            values += [article.title, article.dek]
            values += article.sections.flatMap { [$0.title, $0.text] }
        }
        return values
    }

    private func personRank(_ person: Person) -> Int {
        if person.name.compare(term, options: [.caseInsensitive, .diacriticInsensitive]) == .orderedSame { return 0 }
        if person.call.compare(term, options: [.caseInsensitive, .diacriticInsensitive]) == .orderedSame { return 1 }
        if person.name.localizedStandardContains(term) || person.call.localizedStandardContains(term) { return 2 }
        return 3
    }

    private var allPeople: [Person] {
        store.content.people.filter { includes(personText($0)) }
            .sorted { lhs, rhs in
                let a = personRank(lhs), b = personRank(rhs)
                return a == b ? lhs.name.localizedStandardCompare(rhs.name) == .orderedAscending : a < b
            }
    }
    private var people: [Person] { Array(allPeople.prefix(16)) }

    private var allEvents: [HistoryEvent] {
        store.content.events.filter { event in
            includes([event.title, event.year, event.kind, event.body, event.impact] + event.people.map { store.person($0).name })
        }.sorted {
            if $0.title.localizedStandardContains(term) != $1.title.localizedStandardContains(term) {
                return $0.title.localizedStandardContains(term)
            }
            return EventChronology.precedes($0.year, placement: $0.sortYear, id: $0.id,
                                             $1.year, placement: $1.sortYear, id: $1.id)
        }
    }
    private var events: [HistoryEvent] { Array(allEvents.prefix(20)) }

    private var allArtifacts: [Artifact] {
        store.content.objects.filter { object in
            includes([object.title, object.subtitle, object.body, object.note] + object.people.map { store.person($0).name })
        }
    }
    private var artifacts: [Artifact] { Array(allArtifacts.prefix(16)) }

    private var allTombs: [Tomb] {
        (store.content.tombs ?? []).filter { tomb in
            includes([tomb.title, tomb.area, tomb.location, tomb.status, tomb.body, tomb.note, store.person(tomb.person).name])
        }
    }
    private var tombs: [Tomb] { Array(allTombs.prefix(12)) }

    private var allDynasties: [Dynasty] {
        (store.content.dynasties ?? []).filter { includes([$0.name, $0.years, $0.note]) }
    }
    private var dynasties: [Dynasty] { Array(allDynasties.prefix(16)) }

    private var allSites: [PrehistorySite] {
        (store.content.prehistorySites ?? []).filter {
            includes([$0.name, $0.period, $0.location, $0.province, $0.summary, $0.significance])
        }
    }
    private var sites: [PrehistorySite] { Array(allSites.prefix(12)) }

    private var allTopics: [EraTopic] {
        (store.zhouGuide?.topics ?? []).filter { topic in
            includes([topic.name, topic.call, topic.years, topic.category, topic.summary] + topic.sections.flatMap { [$0.title, $0.text] })
        }
    }
    private var topics: [EraTopic] { Array(allTopics.prefix(12)) }

    private var displayedResultCount: Int {
        people.count + events.count + artifacts.count + tombs.count + dynasties.count + sites.count + topics.count
    }
    private var totalResultCount: Int {
        allPeople.count + allEvents.count + allArtifacts.count + allTombs.count + allDynasties.count + allSites.count + allTopics.count
    }

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 26) {
                if term.isEmpty {
                    introduction
                } else if totalResultCount == 0 {
                    noResults
                } else {
                    Text(displayedResultCount < totalResultCount
                         ? "找到 \(totalResultCount) 项，显示相关度较高的前 \(displayedResultCount) 项"
                         : "找到 \(totalResultCount) 项相关内容")
                        .font(.subheadline).foregroundStyle(Theme.muted)
                        .accessibilityIdentifier("searchResultCount")
                    if !people.isEmpty { peopleSection }
                    if !events.isEmpty { eventsSection }
                    if !artifacts.isEmpty || !tombs.isEmpty { heritageSection }
                    if !dynasties.isEmpty || !sites.isEmpty || !topics.isEmpty { periodSection }
                }
            }
            .padding(.horizontal, 24).padding(.top, 18).padding(.bottom, Theme.pageBottom)
        }
        .background(Theme.paper)
        .foregroundStyle(Theme.text)
        .navigationTitle("全局检索")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(Theme.paper, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always), prompt: "人物、事件、遗珍、陵寝")
    }

    private var introduction: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("从全部历史内容中查找")
                .font(.system(.title2, design: .serif).weight(.semibold)).foregroundStyle(Theme.ink)
            Text("可以输入人物姓名、年号、事件、典籍、器物、遗址或陵寝。结果会保留所属朝代和年代，方便判断同名人物与相近事件。")
                .font(.body).lineSpacing(6).foregroundStyle(Theme.text)
            Text("例如：高骈、咸通、营造法式、平夏城")
                .font(.subheadline).foregroundStyle(Theme.muted)
        }
        .padding(.top, 10)
        .accessibilityIdentifier("searchIntroduction")
    }

    private var noResults: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("未找到相关内容")
                .font(.system(.title3, design: .serif).weight(.semibold)).foregroundStyle(Theme.ink)
            Text("可以换用人物姓名、常用称号、年号或更短的关键词。")
                .font(.body).foregroundStyle(Theme.muted)
        }.padding(.top, 12)
    }

    private var peopleSection: some View {
        SearchSection(title: "人物", displayed: people.count, total: allPeople.count, identifier: "searchSectionCount_people") {
            ForEach(people) { person in
                SearchResultLink(
                    route: .person(person.id),
                    eyebrow: store.dynastyName(store.dynastyID(for: person.id)),
                    title: person.name,
                    subtitle: [person.call, person.kind].filter { !$0.isEmpty }.joined(separator: "　"),
                    identifier: "search_person_\(person.id)"
                )
            }
        }
    }

    private var eventsSection: some View {
        SearchSection(title: "历史事件", displayed: events.count, total: allEvents.count, identifier: "searchSectionCount_events") {
            ForEach(events) { event in
                SearchResultLink(
                    route: .event(event.id),
                    eyebrow: [event.year, event.category ?? event.kind].filter { !$0.isEmpty }.joined(separator: "　"),
                    title: event.title,
                    subtitle: event.body,
                    identifier: "search_event_\(event.id)"
                )
            }
        }
    }

    private var heritageSection: some View {
        SearchSection(title: "遗珍与陵寝", displayed: artifacts.count + tombs.count, total: allArtifacts.count + allTombs.count, identifier: "searchSectionCount_heritage") {
            ForEach(artifacts) { object in
                SearchResultLink(route: .object(object.id), eyebrow: "遗珍", title: object.title, subtitle: object.subtitle, identifier: "search_object_\(object.id)")
            }
            ForEach(tombs) { tomb in
                SearchResultLink(route: .tomb(tomb.id), eyebrow: "陵寝　\(tomb.location)", title: tomb.title, subtitle: tomb.status, identifier: "search_tomb_\(tomb.id)")
            }
        }
    }

    private var periodSection: some View {
        SearchSection(title: "时期与专题", displayed: dynasties.count + sites.count + topics.count, total: allDynasties.count + allSites.count + allTopics.count, identifier: "searchSectionCount_periods") {
            ForEach(dynasties) { dynasty in
                SearchResultLink(route: .dynasty(dynasty.id), eyebrow: dynasty.years, title: dynasty.name, subtitle: dynasty.note, identifier: "search_dynasty_\(dynasty.id)")
            }
            ForEach(sites) { site in
                SearchResultLink(route: .prehistorySite(site.id), eyebrow: "史前遗址　\(site.province)", title: site.name, subtitle: site.period, identifier: "search_site_\(site.id)")
            }
            ForEach(topics) { topic in
                SearchResultLink(route: .eraTopic(topic.id), eyebrow: topic.period ?? topic.category, title: topic.name, subtitle: topic.call, identifier: "search_topic_\(topic.id)")
            }
        }
    }
}

private struct SearchSection<Content: View>: View {
    let title: String
    let displayed, total: Int
    let identifier: String
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .firstTextBaseline) {
                Text(title).font(.system(.title3, design: .serif).weight(.semibold)).foregroundStyle(Theme.ink)
                Spacer()
                Text(displayed < total ? "\(displayed)/\(total)项" : "\(total)项")
                    .font(.caption.monospacedDigit()).foregroundStyle(Theme.muted)
                    .accessibilityIdentifier(identifier)
            }
            VStack(alignment: .leading, spacing: 18) { content }
                .padding(18)
                .background(.white.opacity(0.46), in: RoundedRectangle(cornerRadius: 6))
        }
    }
}

private struct SearchResultLink: View {
    let route: DetailRoute
    let eyebrow, title, subtitle, identifier: String

    var body: some View {
        NavigationLink(value: route) {
            VStack(alignment: .leading, spacing: 6) {
                Text(eyebrow).font(.caption).foregroundStyle(Theme.cinnabar)
                Text(title).font(.headline).foregroundStyle(Theme.ink).frame(maxWidth: .infinity, alignment: .leading)
                if !subtitle.isEmpty {
                    Text(subtitle).font(.subheadline).foregroundStyle(Theme.muted).lineLimit(2).lineSpacing(3)
                }
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(QuietRowStyle())
        .accessibilityIdentifier(identifier)
    }
}
