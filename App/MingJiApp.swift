import SwiftUI

@main struct MingJiApp: App {
    private let result = Result { try HistoryStore() }
    var body: some Scene {
        WindowGroup {
            switch result {
            case .success(let store): RootView(store: store)
            case .failure: ContentUnavailableView("内容未能载入", systemImage: "book.closed", description: Text("本地资料读取失败，请重新安装应用。"))
            }
        }
    }
}
enum DetailRoute: Hashable {
    case personSection(String, PersonSection), relatives(String, FamilyGroup)
    case personEvents(String, MajorEventCategory)
    case person(String), family(String), connections(String), event(String), object(String), tomb(String), article(String), portrait(String)
    case dynasty(String), prehistorySite(String), eraTopic(String), collectionCategory(String, String), about
}
struct RootView: View {
    let store: HistoryStore
    @State private var selectedDynasty: String
    @State private var selected: String
    @State private var tab = 0
    @State private var dynastyPath: [DetailRoute] = []
    @State private var familyPath: [DetailRoute] = []
    @State private var sequencePath: [DetailRoute] = []
    @State private var collectionPath: [DetailRoute] = []
    init(store: HistoryStore) {
        self.store = store
        let savedDynasty = UserDefaults.standard.string(forKey: "selectedDynasty") ?? "ming"
        let dynasty = ["ming", "qing"].contains(savedDynasty) ? savedDynasty : "ming"
        _selectedDynasty = State(initialValue: dynasty)
        _selected = State(initialValue: store.defaultPerson(in: dynasty))
    }
    var body: some View {
        TabView(selection: $tab) {
            NavigationStack(path: $dynastyPath) {
                DynastyPage(store: store, selectedDynasty: $selectedDynasty, path: $dynastyPath)
                    .navigationDestination(for: DetailRoute.self) { RouteDestination(route: $0, store: store, path: $dynastyPath) }
            }.tabItem { Label("朝代", systemImage: "clock") }.tag(0)
            NavigationStack(path: $sequencePath) {
                SuccessionPage(store: store, dynastyID: selectedDynasty)
                    .navigationDestination(for: DetailRoute.self) { RouteDestination(route: $0, store: store, path: $sequencePath) }
            }.tabItem { Label("帝序", systemImage: "list.number") }.tag(1)
            NavigationStack(path: $familyPath) {
                FamilyPage(store: store, selected: $selected, path: $familyPath, isRoot: true, dynastyID: selectedDynasty)
                    .navigationDestination(for: DetailRoute.self) { RouteDestination(route: $0, store: store, path: $familyPath) }
            }.tabItem { Label("家族", systemImage: "point.3.connected.trianglepath.dotted") }.tag(2)
            NavigationStack(path: $collectionPath) {
                CollectionPage(store: store, dynastyID: selectedDynasty)
                    .navigationDestination(for: DetailRoute.self) { RouteDestination(route: $0, store: store, path: $collectionPath) }
            }.tabItem { Label("遗珍", systemImage: "building.columns") }.tag(3)
        }.tint(Theme.cinnabar).preferredColorScheme(.light)
            .onAppear {
                if ProcessInfo.processInfo.arguments.contains("--uitesting") {
                    // Keep UI tests independent while still allowing an explicit
                    // second launch without --uitesting to verify persistence.
                    let defaults = UserDefaults.standard
                    defaults.removeObject(forKey: "selectedDynasty")
                    selectedDynasty = "ming"; selected = "yuanzhang"; tab = 0
                }
            }
            .onChange(of: selectedDynasty) { _, dynasty in
                UserDefaults.standard.set(dynasty, forKey: "selectedDynasty")
                selected = store.defaultPerson(in: dynasty)
                familyPath.removeAll(); sequencePath.removeAll(); collectionPath.removeAll()
            }
            .onChange(of: tab) { _, newTab in
                NotificationCenter.default.post(name: .stopArticleNarration, object: nil)
                if newTab == 2 {
                    selected = store.defaultPerson(in: selectedDynasty)
                    familyPath.removeAll()
                }
            }
    }
}
struct DynastyPage: View {
    let store: HistoryStore
    @Binding var selectedDynasty: String
    @Binding var path: [DetailRoute]
    @State private var lastOpenedDynasty: String?
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 0) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("中国历史").font(.system(.largeTitle, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                    Text("沿年代看王朝更替，也看见并立与转折。").font(.body).foregroundStyle(Theme.text).lineSpacing(5)
                }.padding(.bottom, 26)
                ForEach(store.content.dynasties ?? []) { dynasty in
                    DynastyRow(dynasty: dynasty, isSelected: dynasty.id == (lastOpenedDynasty ?? selectedDynasty)) {
                        lastOpenedDynasty = dynasty.id
                        if dynasty.selectable { selectedDynasty = dynasty.id }
                        path.append(.dynasty(dynasty.id))
                    }
                    Rectangle().fill(Theme.line.opacity(0.5)).frame(height: 0.5)
                }
            }.padding(.horizontal, 24).padding(.vertical, 22)
        }.background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle("史迹").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .toolbar { ToolbarItem(placement: .topBarTrailing) { NavigationLink(value: DetailRoute.about) { Image(systemName: "info.circle") }.accessibilityLabel("阅读说明") } }
            .accessibilityIdentifier("dynastyPage")
    }
}
struct DynastyRow: View {
    let dynasty: Dynasty
    let isSelected: Bool
    @Environment(\.dynamicTypeSize) private var typeSize
    let action: () -> Void
    @State private var feedbackToken = 0
    var body: some View {
        Button {
            feedbackToken += 1
            action()
        } label: { row }
        .buttonStyle(DynastyRowPressStyle())
        .sensoryFeedback(.selection, trigger: feedbackToken)
        .accessibilityLabel("\(dynasty.name)，\(dynasty.years)，打开介绍")
        .accessibilityValue(isSelected ? "已选中" : "")
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityIdentifier("dynasty_\(dynasty.id)")
    }
    private var row: some View {
        let layout = typeSize.isAccessibilitySize ? AnyLayout(VStackLayout(alignment: .leading, spacing: 8)) : AnyLayout(HStackLayout(alignment: .center, spacing: 16))
        return layout {
            Text(dynasty.name)
                .font(.system(.title3, design: .serif).weight(isSelected ? .semibold : .medium))
                .foregroundStyle(isSelected ? Theme.cinnabar : Theme.ink)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text(dynasty.years).font(.caption.monospacedDigit())
                .foregroundStyle(isSelected ? Theme.cinnabar : Theme.muted)
                .multilineTextAlignment(typeSize.isAccessibilitySize ? .leading : .trailing)
                .fixedSize(horizontal: false, vertical: true)
            if isSelected {
                VStack(spacing: -1) {
                    Text("当")
                    Text("前")
                }
                .font(.system(size: 9, design: .serif).weight(.medium))
                .foregroundStyle(Theme.cinnabar)
                .frame(width: 24, height: 36)
                .overlay { Rectangle().stroke(Theme.cinnabar.opacity(0.82), lineWidth: 0.8) }
                .transition(.opacity.combined(with: .scale(scale: 0.9)))
                .accessibilityHidden(true)
            }
        }
        .padding(.vertical, 20).padding(.horizontal, 16)
        .background(isSelected ? Theme.cinnabar.opacity(0.025) : Color.clear)
        .animation(.easeOut(duration: 0.22), value: isSelected)
        .contentShape(Rectangle())
    }
}
private struct DynastyRowPressStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.985 : 1, anchor: .leading)
            .opacity(configuration.isPressed ? 0.68 : 1)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.12), value: configuration.isPressed)
    }
}
struct RouteDestination: View {
    let route: DetailRoute
    let store: HistoryStore
    @Binding var path: [DetailRoute]
    var body: some View {
        switch route {
        case .dynasty(let id): DynastyDetailPage(store: store, dynastyID: id)
        case .prehistorySite(let id): PrehistorySitePage(store: store, siteID: id)
        case .eraTopic(let id): EraTopicPage(store: store, topicID: id)
        case .collectionCategory(let dynastyID, let id):
            if let category = CollectionCategory(rawValue: id) {
                CollectionCategoryPage(store: store, dynastyID: dynastyID, category: category)
            }
        case .person(let id): PersonPage(store: store, personID: id)
        case .personSection(let id, let section): PersonSectionPage(store: store, personID: id, section: section)
        case .personEvents(let id, let category): PersonSectionPage(store: store, personID: id, section: .events, initialEventCategory: category)
        case .relatives(let id, let group): FamilyMembersPage(store: store, personID: id, group: group)
        case .family(let id): LocalFamilyPage(store: store, initial: id, path: $path)
        case .article(let id): ArticleReader(store: store, personID: id)
        case .portrait(let id): PortraitPage(store: store, personID: id)
        case .connections(let id): ConnectionsPage(store: store, personID: id)
        default: DetailScreen(route: route, store: store)
        }
    }
}
struct LocalFamilyPage: View {
    let store: HistoryStore
    @State private var selected: String
    @Binding var path: [DetailRoute]
    init(store: HistoryStore, initial: String, path: Binding<[DetailRoute]>) {
        self.store = store; _selected = State(initialValue: initial); _path = path
    }
    var body: some View { FamilyPage(store: store, selected: $selected, path: $path, isRoot: false, dynastyID: store.dynastyID(for: selected)) }
}
struct FamilyPage: View {
    let store: HistoryStore
    @Binding var selected: String
    @Binding var path: [DetailRoute]
    let isRoot: Bool
    let dynastyID: String
    @State private var trail: [String] = []
    @State private var edge: Edge = .trailing
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var typeSize
    var p: Person { store.person(selected) }
    func focus(_ id: String, from direction: Edge) {
        guard id != selected else { return }
        trail.append(selected); edge = direction
        withAnimation(reduceMotion ? nil : .easeInOut(duration: 0.24)) { selected = id }
    }
    func swipe(_ value: DragGesture.Value) {
        guard abs(value.translation.width) > 60, abs(value.translation.width) > abs(value.translation.height) * 1.8 else { return }
        let peers = (store.siblings(p) + [p]).sorted { ($0.birthOrder ?? 99) < ($1.birthOrder ?? 99) }
        guard let i = peers.firstIndex(where: { $0.id == selected }) else { return }
        let next = i + (value.translation.width < 0 ? 1 : -1)
        if peers.indices.contains(next) { focus(peers[next].id, from: value.translation.width < 0 ? .trailing : .leading) }
    }
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                if let previous = trail.last {
                    Button {
                        _ = trail.popLast(); edge = .leading
                        withAnimation(reduceMotion ? nil : .easeInOut(duration: 0.24)) { selected = previous }
                    } label: { Label("返回 \(store.person(previous).name)", systemImage: "arrow.uturn.backward") }
                        .font(.subheadline).frame(minHeight: 44).accessibilityIdentifier("historyBack")
                }
                graph
                if !store.siblings(p).isEmpty { siblings }
            }.padding(.horizontal, 24).padding(.top, 14).padding(.bottom, 72)
        }.background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle(isRoot ? (dynastyID == "qing" ? "清朝家族" : "明朝家族") : "\(p.name)家族").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .toolbar { if isRoot { ToolbarItem(placement: .topBarTrailing) { NavigationLink(value: DetailRoute.about) { Image(systemName: "info.circle").font(.system(size: 17)) }.accessibilityLabel("阅读说明") } } }
    }
    var graph: some View {
        VStack(spacing: 0) {
            let parents = store.parents(selected)
            if !parents.isEmpty && !typeSize.isAccessibilitySize {
                familySectionHeading("祖先", detail: "父母与上一代")
                HStack(alignment: .top, spacing: 12) {
                    ForEach(parents) { link in
                        node(store.person(link.to), label: store.parentLabel(link.kind), direction: .top)
                    }
                }
                BranchConnector(count: parents.count, upward: true).frame(height: 30)
            }
            hero.id(selected)
                .transition(reduceMotion ? .identity : .asymmetric(insertion: .move(edge: edge).combined(with: .opacity), removal: .opacity))
            if typeSize.isAccessibilitySize && !parents.isEmpty {
                VStack(spacing: 10) {
                    familySectionHeading("祖先", detail: "父母与上一代")
                    ForEach(parents) { link in
                        node(store.person(link.to), label: store.parentLabel(link.kind), direction: .top)
                    }
                }.padding(.top, 16)
            }
            let spouses = store.spouses(selected)
            if !spouses.isEmpty {
                let layout = typeSize.isAccessibilitySize ? AnyLayout(VStackLayout(alignment: .leading, spacing: 10)) : AnyLayout(HStackLayout(spacing: 10))
                layout {
                    Rectangle().fill(Theme.line).frame(width: 22, height: 1)
                    Text("配偶").font(.caption).foregroundStyle(Theme.muted)
                    ForEach(spouses) { person in
                        Button { focus(person.id, from: .trailing) } label: { Text(person.name).font(.subheadline).padding(.horizontal, 10).frame(minHeight: 44).background(.white.opacity(0.5)) }
                            .accessibilityIdentifier("relative_\(person.id)")
                    }
                    Spacer(minLength: 0)
                }.padding(.top, 8)
            }
            let children = store.children(selected)
            if !children.isEmpty {
                BranchConnector(count: 1, upward: false).frame(height: 22)
                HStack(alignment: .firstTextBaseline) {
                    familySectionHeading("子女", detail: "\(children.count)位，按已知排行")
                    Spacer(minLength: 12)
                    NavigationLink(value: DetailRoute.relatives(selected, .children)) {
                        Text("查看排行").font(.caption).foregroundStyle(Theme.cinnabar).frame(minHeight: 44)
                    }
                    .buttonStyle(QuietRowStyle())
                    .accessibilityIdentifier("allChildren")
                }
                let columns = typeSize.isAccessibilitySize ? [GridItem(.flexible())] : [GridItem(.flexible(), spacing: 12), GridItem(.flexible())]
                LazyVGrid(columns: columns, alignment: .leading, spacing: 12) {
                    ForEach(children) { child in childNode(child) }
                }
            }
        }.accessibilityElement(children: .contain)
    }
    func familySectionHeading(_ title: String, detail: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
            Text(detail).font(.caption2).foregroundStyle(Theme.muted)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.bottom, 10)
    }
    func childNode(_ person: Person) -> some View {
        Button { focus(person.id, from: .bottom) } label: {
            VStack(alignment: .leading, spacing: 5) {
                Text(store.orderLabel(person)).font(.caption2).foregroundStyle(Theme.cinnabar)
                Text(person.name.replacingOccurrences(of: "爱新觉罗·", with: ""))
                    .font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                Text(person.call).font(.caption2).foregroundStyle(Theme.muted).lineLimit(1)
            }
            .frame(maxWidth: .infinity, minHeight: 62, alignment: .leading)
            .padding(.horizontal, 12).padding(.vertical, 10)
            .background(.white.opacity(0.48))
            .overlay { Rectangle().stroke(Theme.line.opacity(0.42), lineWidth: 0.5) }
        }
        .buttonStyle(QuietRowStyle())
        .accessibilityIdentifier("relative_\(person.id)")
        .accessibilityLabel("\(store.orderLabel(person))，\(person.name)，切换人物")
    }
    var hero: some View {
        Group {
            if typeSize.isAccessibilitySize {
                VStack(alignment: .leading, spacing: 16) {
                    HStack(alignment: .top, spacing: 16) { LocalImage(name: store.image(selected), compact: true).frame(width: 72, height: 100); Text(p.name).font(.system(.title, design: .serif)) }
                    heroDetails
                }
            } else {
                HStack(alignment: .center, spacing: 20) {
                    LocalImage(name: store.image(selected)).frame(width: 108, height: 154)
                    VStack(alignment: .leading, spacing: 10) { Text(p.name).font(.system(.title, design: .serif)); heroDetails }.frame(maxWidth: .infinity, alignment: .leading)
                }
            }
        }.padding(20).frame(maxWidth: .infinity, alignment: .leading).background(Theme.ink, in: RoundedRectangle(cornerRadius: 8)).foregroundStyle(Theme.paper)
            .contentShape(Rectangle())
            .onTapGesture { path.append(.person(selected)) }
            .simultaneousGesture(DragGesture(minimumDistance: 20).onEnded(swipe))
            .accessibilityElement(children: .ignore).accessibilityLabel("\(p.name)，\(p.call)，\(store.portrait(selected)?.displayLabel ?? "")，展开人物")
            .accessibilityAddTraits(.isButton).accessibilityAction { path.append(.person(selected)) }.accessibilityIdentifier("personHero")
    }
    var heroDetails: some View {
        VStack(alignment: .leading, spacing: 7) {
            Text(p.call).font(.subheadline)
            if let label = store.portrait(selected)?.displayLabel { Text(label).font(.caption).foregroundStyle(Theme.paper.opacity(0.85)) }
            if p.kind == "皇帝" { Text("在位 \(p.reign)").font(.caption).monospacedDigit() }
            else { Text(p.kind).font(.caption) }
            Text("人物详情").font(.caption.weight(.medium)).foregroundStyle(Theme.paper.opacity(0.72)).padding(.top, 5)
        }
    }
    func node(_ person: Person, label: String, direction: Edge) -> some View {
        Button { focus(person.id, from: direction) } label: {
            VStack(alignment: .leading, spacing: 6) {
                Text(label).font(.caption).foregroundStyle(Theme.muted)
                Text(person.name).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                if !typeSize.isAccessibilitySize && !person.call.contains(label) && !person.call.contains("母亲") && !person.call.contains("父亲") { Text(person.call).font(.caption2).foregroundStyle(Theme.muted) }
            }.frame(maxWidth: .infinity, minHeight: 56, alignment: .leading).padding(12).background(.white.opacity(0.55))
        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("relative_\(person.id)").accessibilityLabel("\(label)，\(person.name)，切换人物")
    }
    var siblings: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack { Text("同辈").font(.subheadline); Spacer(); if !typeSize.isAccessibilitySize { Text("可左右轻扫人物卡").font(.caption).foregroundStyle(Theme.muted) } }
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 14) {
                    ForEach(store.siblings(p)) { person in
                        Button { focus(person.id, from: .trailing) } label: {
                            HStack(spacing: 8) { Text(store.siblingLabel(person, relativeTo: p)).foregroundStyle(Theme.muted); Text(person.name) }.font(.subheadline).padding(.horizontal, 14).frame(minHeight: 48).background(.white.opacity(0.5))
                        }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("relative_\(person.id)")
                    }
                }
            }
        }
    }
}
struct BranchConnector: View {
    let count: Int
    let upward: Bool
    var body: some View {
        GeometryReader { g in
            Path { path in
                let mid = g.size.width / 2, height = g.size.height, branchY = height / 2
                let stemY: CGFloat = upward ? height : 0
                let endY: CGFloat = upward ? 0 : height
                path.move(to: CGPoint(x: mid, y: stemY)); path.addLine(to: CGPoint(x: mid, y: branchY))
                for i in 0..<max(1, count) {
                    let x = g.size.width * (CGFloat(i) + 0.5) / CGFloat(max(1, count))
                    path.move(to: CGPoint(x: mid, y: branchY)); path.addLine(to: CGPoint(x: x, y: branchY)); path.addLine(to: CGPoint(x: x, y: endY))
                }
            }.stroke(Theme.line, lineWidth: 1)
        }.accessibilityHidden(true)
    }
}
func sectionTitle(_ title: String) -> some View { Text(title).font(.system(.title3, design: .serif).weight(.medium)).foregroundStyle(Theme.ink).padding(.bottom, 8) }
struct EventRow: View {
    let event: HistoryEvent
    var body: some View {
        NavigationLink(value: DetailRoute.event(event.id)) {
            HStack(alignment: .top, spacing: 16) {
                VStack(alignment: .leading, spacing: 7) { Text(event.year).font(.caption).foregroundStyle(Theme.cinnabar); Text(event.title).font(.body).foregroundStyle(Theme.text) }
                Spacer()
            }.frame(maxWidth: .infinity, minHeight: 48, alignment: .leading).padding(.vertical, 12).contentShape(Rectangle())
        }.buttonStyle(QuietRowStyle()).overlay(alignment: .bottom) { Rectangle().fill(Theme.line.opacity(0.45)).frame(height: 0.5) }
            .accessibilityIdentifier("event_\(event.id)")
    }
}
struct SuccessionPage: View {
    let store: HistoryStore
    let dynastyID: String
    @Environment(\.dynamicTypeSize) private var typeSize
    var items: [Succession] { store.sequence(in: dynastyID) }
    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 0) {
                Text(dynastyID == "qing" ? "从后金兴起到帝制终结，皇位传承始终与宗室、摄政和时代转折相连。努尔哈赤与皇太极属于入关前的两代统治者。" : "从洪武开国到崇祯亡国，明代皇位大体沿朱元璋一系传承，也经历靖难、土木堡之变与复辟等重要转折。朱祁镇两度在位，在序列中分段呈现。")
                    .font(.subheadline).foregroundStyle(Theme.muted).padding(.bottom, 20).fixedSize(horizontal: false, vertical: true)
                ForEach(items) { item in
                    let p = store.person(item.person)
                    NavigationLink(value: DetailRoute.family(p.id)) {
                        SuccessionRow(
                            person: p,
                            item: item,
                            imageName: store.image(p.id),
                            hidesPortrait: typeSize.isAccessibilitySize
                        )
                    }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("succession_\(item.id)")
                    Rectangle().fill(Theme.line.opacity(0.46)).frame(height: 0.5).padding(.leading, typeSize.isAccessibilitySize ? 0 : 78)
                }
                Text(dynastyID == "qing" ? "努尔哈赤生前为后金大汗；1636年皇太极改国号为清。公历年概括实际统治，摄政与太上皇掌权另在人物和事件中说明。" : "公历年概括实际在位；同年交接不表示全年同时在位。年号起讫与实际在位年份分别列示。")
                    .font(.caption).foregroundStyle(Theme.muted).padding(.top, 22).fixedSize(horizontal: false, vertical: true)
            }.padding(24)
        }.background(Theme.paper).foregroundStyle(Theme.text).navigationTitle(dynastyID == "qing" ? "清朝帝序" : "明朝帝序").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .accessibilityIdentifier("successionPage_\(dynastyID)")
    }
}

private struct SuccessionRow: View {
    let person: Person
    let item: Succession
    let imageName: String?
    let hidesPortrait: Bool

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            if !hidesPortrait {
                LocalImage(name: imageName, compact: true)
                    .frame(width: 62, height: 82)
                    .background(.white.opacity(0.34))
                    .clipShape(Rectangle())
                    .overlay { Rectangle().stroke(Theme.line.opacity(0.54), lineWidth: 0.5) }
                    .accessibilityHidden(true)
            }

            VStack(alignment: .leading, spacing: 0) {
                Text(person.name)
                    .font(.system(.title3, design: .serif).weight(.semibold))
                    .foregroundStyle(Theme.ink)
                    .fixedSize(horizontal: false, vertical: true)

                HStack(alignment: .firstTextBaseline, spacing: 12) {
                    Text("年号 \(eraName)")
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(Theme.cinnabar)
                        .accessibilityIdentifier("successionEra_\(item.id)")
                    Spacer(minLength: 8)
                    if !person.temple.isEmpty {
                        Text("庙号 \(person.temple)")
                            .font(.caption)
                            .foregroundStyle(Theme.muted)
                            .multilineTextAlignment(.trailing)
                            .accessibilityIdentifier("successionTemple_\(item.id)")
                    }
                }
                    .padding(.top, 7)

                HStack(alignment: .firstTextBaseline, spacing: 12) {
                    Text("在位 \(item.years)")
                        .font(.caption.monospacedDigit())
                        .foregroundStyle(Theme.muted)
                        .accessibilityIdentifier("successionReign_\(item.id)")
                    Spacer(minLength: 6)
                    Text(transitionText)
                        .font(.caption)
                        .foregroundStyle(Theme.muted)
                        .multilineTextAlignment(.trailing)
                        .lineLimit(2)
                }
                .padding(.top, 8)
            }
            .frame(maxWidth: .infinity, minHeight: hidesPortrait ? 84 : 82, alignment: .topLeading)
        }
        .padding(.vertical, 16)
        .contentShape(Rectangle())
        .accessibilityElement(children: .contain)
    }

    private var eraName: String {
        if person.id == "qizhen" { return item.id == "7" ? "天顺" : "正统" }
        return person.era.split(separator: " ").first.map(String.init) ?? person.era
    }

    private var transitionText: String {
        switch item.transition {
        case "开创后金": return "开创后金"
        case "父 → 子": return "父子相承"
        case "父 → 子 · 受禅即位": return "父子相承，受禅即位"
        case "祖父 → 孙": return "祖孙相承"
        case "侄 → 叔 · 靖难夺位": return "靖难夺位"
        case "父 → 子 · 首次在位": return "父子相承，首次在位"
        case "兄 → 弟 · 土木之变后": return "土木之变后入继"
        case "弟 → 兄 · 夺门复位": return "夺门复位"
        case "兄 → 弟": return "兄弟相继"
        case "堂兄 → 堂弟": return "旁支入继"
        case "堂兄 → 堂弟 · 嗣子入继": return "堂弟以嗣子入继"
        case "叔 → 侄 · 兼祧入继": return "侄辈兼祧入继"
        default:
            return item.transition
                .replacingOccurrences(of: " → ", with: "至")
                .replacingOccurrences(of: " · ", with: "，")
        }
    }
}
struct CollectionPage: View {
    let store: HistoryStore
    let dynastyID: String

    private var categories: [CollectionCategory] {
        CollectionCategory.allCases.filter { $0 == .tombs || !artifacts(for: $0).isEmpty }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Text(dynastyID == "qing" ? "从思想、器物与陵寝，理解清代的制度、生活与时代转折。" : "从思想、器物与陵寝，理解明代的知识、工艺与社会面貌。")
                    .font(.subheadline).foregroundStyle(Theme.muted).lineSpacing(4).padding(.bottom, 24)
                ForEach(categories) { category in
                    NavigationLink(value: DetailRoute.collectionCategory(dynastyID, category.rawValue)) {
                        VStack(alignment: .leading, spacing: 7) {
                            Text(category.title).font(.system(.title2, design: .serif).weight(.medium)).foregroundStyle(Theme.ink)
                            Text(category.note).font(.subheadline).foregroundStyle(Theme.muted)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 22)
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(QuietRowStyle()).accessibilityIdentifier("collectionCategory_\(category.rawValue)")
                    Rectangle().fill(Theme.line.opacity(0.5)).frame(height: 0.5)
                }
            }.padding(.horizontal, 24).padding(.top, 24).padding(.bottom, 70)
        }
        .background(Theme.paper).foregroundStyle(Theme.text)
        .navigationTitle(dynastyID == "qing" ? "清朝遗珍" : "明朝遗珍").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
        .accessibilityIdentifier("collectionPage_\(dynastyID)")
    }

    private func artifacts(for category: CollectionCategory) -> [Artifact] {
        store.objects(in: dynastyID).filter { object in
            switch category {
            case .ideas: return Self.isIdea(object)
            case .objects: return !Self.isIdea(object) && !Self.isBook(object) && !Self.isArchitecture(object)
            case .texts: return Self.isBook(object)
            case .architecture: return Self.isArchitecture(object)
            case .tombs: return false
            }
        }
    }
    fileprivate static func isBook(_ object: Artifact) -> Bool {
        object.symbol == "book.closed" || object.symbol == "music.note" || object.symbol == "doc.text"
    }
    fileprivate static func isArchitecture(_ object: Artifact) -> Bool { object.symbol.hasPrefix("building.columns") }
    fileprivate static func isIdea(_ object: Artifact) -> Bool { object.symbol == "brain.head.profile" }
}

private enum CollectionCategory: String, CaseIterable, Identifiable {
    case ideas, objects, texts, architecture, tombs
    var id: String { rawValue }
    var title: String {
        switch self { case .ideas: return "思想与变革"; case .objects: return "器物"; case .texts: return "典籍文书"; case .architecture: return "建筑与纪念"; case .tombs: return "帝王陵寝" }
    }
    var note: String {
        switch self { case .ideas: return "观念如何形成，又如何改变时代"; case .objects: return "瓷器与日常物质遗存"; case .texts: return "制度、知识与艺术文本"; case .architecture: return "宫殿、寺院与纪念空间"; case .tombs: return "陵区、墓主与皇位传承" }
    }
}

private struct CollectionCategoryPage: View {
    let store: HistoryStore
    let dynastyID: String
    let category: CollectionCategory
    @Environment(\.dynamicTypeSize) private var typeSize
    private var artifacts: [Artifact] {
        store.objects(in: dynastyID).filter { object in
            switch category {
            case .ideas: return CollectionPage.isIdea(object)
            case .objects: return !CollectionPage.isIdea(object) && !CollectionPage.isBook(object) && !CollectionPage.isArchitecture(object)
            case .texts: return CollectionPage.isBook(object)
            case .architecture: return CollectionPage.isArchitecture(object)
            case .tombs: return false
            }
        }
    }
    private var areaOrder: [String] {
        dynastyID == "qing" ? ["沈阳 · 盛京三陵", "河北 · 清东陵", "河北 · 清西陵", "特殊安葬"] : ["南京 · 明孝陵", "北京 · 明十三陵", "北京 · 景泰陵", "尚无定论"]
    }
    private func areaParts(_ area: String) -> (place: String?, name: String) {
        let parts = area.components(separatedBy: " · ")
        return parts.count == 2 ? (parts[0], parts[1]) : (nil, area)
    }
    private func reignName(_ person: Person) -> String {
        person.call.replacingOccurrences(of: "皇帝", with: "")
    }
    private func shortName(_ person: Person) -> String {
        person.name.replacingOccurrences(of: "爱新觉罗·", with: "")
    }
    var body: some View {
        ScrollView { if category == .tombs { tombList } else { artifactList } }
            .background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle(category.title).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .accessibilityIdentifier("collectionCategoryPage_\(category.rawValue)")
    }
    private var artifactList: some View {
        LazyVStack(alignment: .leading, spacing: 0) {
            ForEach(artifacts) { object in
                NavigationLink(value: DetailRoute.object(object.id)) {
                    HStack(alignment: .center, spacing: 15) {
                        if let image = object.image, !typeSize.isAccessibilitySize {
                            LocalImage(name: image)
                                .frame(width: 68, height: 80)
                                .background(.white.opacity(0.34))
                                .clipShape(Rectangle())
                                .overlay { Rectangle().stroke(Theme.line.opacity(0.5), lineWidth: 0.5) }
                                .accessibilityHidden(true)
                        }
                        VStack(alignment: .leading, spacing: 6) {
                            Text(object.title).font(.system(.headline, design: .serif)).foregroundStyle(Theme.ink)
                            Text(object.subtitle).font(.subheadline).foregroundStyle(Theme.muted).lineLimit(2)
                        }.frame(maxWidth: .infinity, alignment: .leading)
                    }.padding(.vertical, 17).contentShape(Rectangle())
                }
                .buttonStyle(QuietRowStyle()).accessibilityIdentifier("artifact_\(object.id)")
                Rectangle().fill(Theme.line.opacity(0.48)).frame(height: 0.5)
            }
        }.padding(.horizontal, 24).padding(.top, 10).padding(.bottom, 70)
    }
    private var tombList: some View {
        LazyVStack(alignment: .leading, spacing: 42) {
            ForEach(areaOrder, id: \.self) { area in
                let tombs = store.tombs(in: dynastyID).filter { $0.area == area }
                let heading = areaParts(area)
                if !tombs.isEmpty {
                    VStack(alignment: .leading, spacing: 0) {
                        VStack(alignment: .leading, spacing: 4) {
                            if let place = heading.place {
                                Text(place).font(.caption.weight(.medium)).foregroundStyle(Theme.cinnabar)
                            }
                            Text(heading.name)
                                .font(.system(.title2, design: .serif).weight(.medium))
                                .foregroundStyle(Theme.ink)
                        }
                        .padding(.bottom, 10)
                        ForEach(tombs) { tomb in
                            let person = store.person(tomb.person)
                            NavigationLink(value: DetailRoute.tomb(tomb.id)) {
                                Group {
                                    if typeSize.isAccessibilitySize {
                                        VStack(alignment: .leading, spacing: 7) {
                                            Text(tomb.title)
                                                .font(.system(.title3, design: .serif).weight(.semibold))
                                                .foregroundStyle(Theme.ink)
                                            Text("\(shortName(person))，\(reignName(person))")
                                                .font(.caption).foregroundStyle(Theme.muted)
                                        }
                                    } else {
                                        HStack(alignment: .firstTextBaseline, spacing: 18) {
                                            Text(tomb.title)
                                                .font(.system(.title3, design: .serif).weight(.semibold))
                                                .foregroundStyle(Theme.ink)
                                            Spacer(minLength: 10)
                                            VStack(alignment: .trailing, spacing: 3) {
                                                Text(shortName(person)).font(.subheadline).foregroundStyle(Theme.text)
                                                Text(reignName(person)).font(.caption).foregroundStyle(Theme.muted)
                                            }
                                        }
                                    }
                                }
                                .frame(maxWidth: .infinity, minHeight: 54, alignment: .leading)
                                .padding(.vertical, 10)
                                .contentShape(Rectangle())
                            }
                            .buttonStyle(QuietRowStyle()).accessibilityIdentifier(tomb.id)
                            Rectangle().fill(Theme.line.opacity(0.42)).frame(height: 0.5)
                        }
                    }
                }
            }
        }.padding(.horizontal, 24).padding(.top, 24).padding(.bottom, 80)
    }
}
