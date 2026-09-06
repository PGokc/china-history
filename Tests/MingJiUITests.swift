import XCTest

final class MingJiUITests: XCTestCase {
    @MainActor func launch(_ large: Bool = false, enterFamily: Bool = true) -> XCUIApplication {
        let app = XCUIApplication(); app.launchArguments = ["--uitesting"]
        if large { app.launchArguments += ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"] }
        app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        if enterFamily { app.tabBars.buttons["家族"].tap(); XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 10)) }
        return app
    }
    @MainActor func shot(_ name: String, _ app: XCUIApplication) {
        Thread.sleep(forTimeInterval: 1)
        let attachment = XCTAttachment(screenshot: app.screenshot()); attachment.name = name; attachment.lifetime = .keepAlways; add(attachment)
        let tree = XCTAttachment(string: app.debugDescription); tree.name = name + "-tree"; tree.lifetime = .keepAlways; add(tree)
    }
    @MainActor func reach(_ element: XCUIElement, in app: XCUIApplication, attempts: Int = 8) {
        for _ in 0..<attempts { if element.isHittable { return }; app.swipeUp() }
        XCTAssertTrue(element.isHittable)
    }
    @MainActor func openArticle(in app: XCUIApplication) {
        if !app.buttons["articleEntry"].exists {
            reach(app.buttons["personHero"], in: app); app.buttons["personHero"].tap()
            XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        }
        reach(app.buttons["articleEntry"], in: app); app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5))
    }
    @MainActor func testV28TimeMapFiltersAndKeepsNavigation() throws {
        let app = launch(enterFamily: false)
        app.buttons["dynasty_prehistory"].tap()
        let slider = app.sliders["historyTimeSlider"]
        XCTAssertTrue(slider.waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["约公元前3000年"].exists)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_liangzhu"].exists)
        XCTAssertFalse(app.buttons["contemporary_hemudu"].exists)
        app.buttons["完成"].tap()
        slider.adjust(toNormalizedSliderPosition: 0)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_hemudu"].exists)
        XCTAssertFalse(app.buttons["contemporary_liangzhu"].exists)
        app.buttons["contemporary_hemudu"].tap()
        XCTAssertTrue(app.navigationBars["河姆渡遗址"].waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.buttons["完成"].tap()
        slider.adjust(toNormalizedSliderPosition: 1)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_shimao"].exists)
        XCTAssertFalse(app.buttons["contemporary_hemudu"].exists)
        app.buttons["完成"].tap()
        app.buttons["远古人类"].tap()
        XCTAssertTrue(app.staticTexts["距今约170万年"].exists)
        app.buttons["contemporarySites"].tap()
        XCTAssertTrue(app.buttons["contemporary_yuanmou"].exists)
        app.buttons["完成"].tap()
        app.buttons["文明起源"].tap()
        shot("v28-time-map", app)
    }
    @MainActor func testV27DynastyMetadataAndMapLinks() throws {
        let app = launch(enterFamily: false)
        XCTAssertFalse(app.staticTexts["正在探索 · 明"].exists)
        app.buttons["dynasty_prehistory"].tap()
        app.buttons["总览"].tap()
        app.swipeUp()
        shot("v27-map-overview", app)
        for _ in 0..<4 {
            let cluster = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@ AND identifier CONTAINS %@", "siteCluster_", "hemudu")).firstMatch
            if !cluster.exists { break }
            cluster.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
            Thread.sleep(forTimeInterval: 1)
        }
        let marker = app.buttons["siteMarker_hemudu"]
        XCTAssertTrue(marker.waitForExistence(timeout: 5))
        shot("v27-map", app)
        marker.tap()
        XCTAssertTrue(app.navigationBars["河姆渡遗址"].waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
        XCTAssertEqual(app.buttons["dynasty_prehistory"].value as? String, "已选中")
        shot("v27-dynasty", app)
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.staticTexts["庙号 太祖"].exists)
        XCTAssertTrue(app.staticTexts["年号 洪武"].exists)
        XCTAssertTrue(app.staticTexts["在位 1368—1398"].exists)
        shot("v27-sequence", app)
    }

    @MainActor func testV30SuccessionUsesCompactHierarchy() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.buttons["succession_0"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["年号 洪武"].exists)
        XCTAssertTrue(app.staticTexts["在位 1368—1398"].exists)
        XCTAssertFalse(app.staticTexts["父 → 子"].exists)

        reach(app.buttons["succession_6"], in: app, attempts: 10)
        XCTAssertTrue(app.staticTexts["年号 景泰"].exists)
        XCTAssertTrue(app.staticTexts["土木之变后入继"].exists)
        XCTAssertFalse(app.staticTexts["后世绣像"].exists)
        shot("v30-sequence-hierarchy", app)
    }

    @MainActor func testV31TombsUseGroupedTwoColumnHierarchy() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap()
        app.buttons["collectionCategory_tombs"].tap()
        XCTAssertTrue(app.navigationBars["帝王陵寝"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["南京"].exists)
        XCTAssertTrue(app.staticTexts["明孝陵"].exists)
        XCTAssertFalse(app.staticTexts["明孝陵（南京）"].exists)
        reach(app.buttons["tomb_di"], in: app, attempts: 5)
        XCTAssertTrue(app.staticTexts["明十三陵"].exists)
        XCTAssertTrue(app.staticTexts["长陵"].exists)
        XCTAssertTrue(app.staticTexts["朱棣"].exists)
        XCTAssertTrue(app.staticTexts["永乐"].exists)
        shot("v31-tomb-hierarchy", app)
    }
    @MainActor func testV25ReadingControls() throws {
        let app = launch(); openArticle(in: app)
        XCTAssertTrue(app.buttons["开始朗读"].isHittable)
        XCTAssertGreaterThanOrEqual(app.buttons["开始朗读"].frame.width, 44)
        app.buttons["朗读设置"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        app.buttons["完成"].tap()
        XCTAssertTrue(app.buttons["articleContents"].isHittable)
        shot("v25-reader", app)
    }
    @MainActor func testFamilyExplorationAndFreshEntry() throws {
        let app = launch(); shot("01-family", app)
        app.buttons["relative_ma"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("马氏"))
        XCTAssertTrue(app.buttons["relative_biao"].exists); shot("02-mother-children",app)
        app.buttons["relative_biao"].tap()
        XCTAssertTrue(app.buttons["relative_ma"].exists)
        app.buttons["relative_yuanzhang"].tap()
        chooseChild("di", in:app)
        app.buttons["relative_gaochi"].tap()
        app.buttons["personHero"].swipeLeft()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱高煦"))
        app.buttons["personHero"].swipeRight()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱高炽"))
        app.buttons["relative_zhanji"].tap()
        app.terminate(); app.launchArguments = []; app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10)); app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 10))
        let founderShown = NSPredicate(format: "label CONTAINS %@", "朱元璋")
        expectation(for: founderShown, evaluatedWith: app.buttons["personHero"])
        waitForExpectations(timeout: 3)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout: 5))
        app.buttons["portraitEntry"].tap(); shot("03-portrait",app)
    }
    @MainActor func testArticleAndChapterRestoration() throws {
        let app = launch(); openArticle(in: app)
        Thread.sleep(forTimeInterval:1)
        app.buttons["articleContents"].tap();app.buttons["开篇"].tap();shot("04-article",app)
        app.buttons["articleContents"].tap()
        app.buttons["1368年为什么值得单独记住"].tap();shot("05-chapter",app)
        XCTAssertTrue(app.staticTexts["1368年为什么值得单独记住"].isHittable)
        app.terminate();app.launch(); XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10)); app.tabBars.buttons["家族"].tap()
        openArticle(in: app)
        Thread.sleep(forTimeInterval:1)
        XCTAssertTrue(app.staticTexts["1368年为什么值得单独记住"].isHittable)
    }
    @MainActor func testV12ArticleNarrationControls() throws {
        let app = launch(); openArticle(in: app)
        XCTAssertTrue(app.buttons["narrationToggle"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["narrationSettings"].exists)
        XCTAssertTrue(app.buttons["narrationPrevious"].exists)
        XCTAssertTrue(app.buttons["narrationNext"].exists)
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        app.buttons["narrationSettings"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["narrationSpeed_标准"].exists)
        app.buttons["完成"].tap()
        app.buttons["narrationToggle"].tap()
        XCTAssertEqual(app.buttons["narrationToggle"].label, "暂停朗读")
        app.tabBars.buttons["朝代"].tap()
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["narrationToggle"].waitForExistence(timeout: 5))
        XCTAssertEqual(app.buttons["narrationToggle"].label, "开始朗读")
        shot("v12-article-narration", app)
    }
    @MainActor func testArtifactAndTombReturnContext() throws {
        let app = launch();app.tabBars.buttons["遗珍"].tap();shot("06-objects",app)
        app.buttons["collectionCategory_objects"].tap()
        app.buttons["artifact_porcelain"].tap()
        XCTAssertTrue(app.staticTexts["观看提示"].waitForExistence(timeout:5));shot("07-object-detail",app)
        reach(app.buttons["explore_zhanji"],in:app);app.buttons["explore_zhanji"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5));XCTAssertTrue(app.buttons["personHero"].label.contains("朱瞻基"))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_zhanji"].waitForExistence(timeout:5));XCTAssertTrue(app.buttons["explore_zhanji"].isHittable)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.buttons["collectionCategory_tombs"].tap();shot("08-tombs",app)
        app.buttons["tomb_yuanzhang"].tap();XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5));shot("09-tomb-detail",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["tomb_yunwen"],in:app);app.buttons["tomb_yunwen"].tap()
        XCTAssertTrue(app.staticTexts["尚无定论"].waitForExistence(timeout:5))
    }
    @MainActor func testLargeTypeReading() throws {
        let app = launch(true);shot("10-large-family",app)
        reach(app.buttons["personHero"],in:app);app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5));shot("11-large-person",app)
        reach(app.buttons["articleEntry"],in:app);app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("12-large-article",app)
    }

    @MainActor func testVerticalDragPreservesFocusedPerson() throws {
        let app = launch()
        chooseChild("di", in:app);app.buttons["relative_gaochi"].tap()
        let hero = app.buttons["personHero"]
        hero.coordinate(withNormalizedOffset: CGVector(dx:0.5,dy:0.8)).press(forDuration:0.05, thenDragTo:hero.coordinate(withNormalizedOffset:CGVector(dx:0.5,dy:0.1)))
        XCTAssertTrue(hero.label.contains("朱高炽"))
        XCTAssertFalse(app.buttons["portraitEntry"].exists)
        app.swipeDown()
        XCTAssertTrue(hero.isHittable)
    }

    @MainActor func testFiguresHaveArticlesAndReturnLinks() throws {
        let app = launch();reach(app.buttons["allAssociates"],in:app);app.buttons["allAssociates"].tap()
        reach(app.buttons["associate_lishanzhang"],in:app);app.buttons["associate_lishanzhang"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("13-figure",app)
        reach(app.buttons["articleEntry"],in:app);app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("14-figure-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        openAssociates(in:app);reach(app.buttons["associate_yuanzhang"],in:app);app.buttons["associate_yuanzhang"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5))
        XCTAssertTrue(app.staticTexts["洪武皇帝"].exists)
    }

    @MainActor func openEmperor(_ sequence: String, in app: XCUIApplication) {
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_" + sequence], in: app)
        app.buttons["succession_" + sequence].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
    }
    @MainActor func testV3ChapterEventPersonReturn() throws {
        let app = launch(); openEmperor("5", in: app)
        shot("v3-01-yingzong-family",app)
        openArticle(in: app)
        Thread.sleep(forTimeInterval:1)
        app.buttons["articleContents"].tap();app.buttons["1449年，御驾成了俘虏"].tap()
        let links = app.buttons["chapterLinks_qizhen-3"]
        reach(links,in:app); links.tap()
        let event = app.buttons["chapterEvent_qizhen-3_v2e_tumu"]
        reach(event,in:app);shot("v3-02-chapter-links",app);event.tap()
        XCTAssertTrue(app.staticTexts["发生了什么"].waitForExistence(timeout:5))
        reach(app.buttons["explore_esen"],in:app);shot("v3-03-event-network",app);app.buttons["explore_esen"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-04-esen",app)
        XCTAssertFalse(app.buttons["explore_esen"].exists)
        app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("v3-05-esen-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_esen"].isHittable)
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(event.isHittable)
    }
    @MainActor func testV3JingtaiConnectionsAndTomb() throws {
        let app = launch();openEmperor("6",in:app)
        app.buttons["personHero"].tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap();app.buttons["tombCard"].tap()
        XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5));shot("v3-06-jingtai-tomb",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap();openAssociates(in:app);reach(app.buttons["associate_yuqian"],in:app);app.buttons["associate_yuqian"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-07-yuqian",app)
        XCTAssertFalse(app.buttons["explore_yuqian"].exists)
        openAssociates(in:app);reach(app.buttons["associate_jianshen"],in:app);app.buttons["associate_jianshen"].tap()
        XCTAssertTrue(app.buttons["portraitEntry"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["associate_jianshen"].isHittable)
    }
    @MainActor func testV3TempleToPeopleLoop() throws {
        let app = launch();app.tabBars.buttons["遗珍"].tap()
        reach(app.buttons["artifact_zhihua"],in:app);app.buttons["artifact_zhihua"].tap()
        XCTAssertTrue(app.staticTexts["观看提示"].waitForExistence(timeout:5));shot("v3-08-zhihua",app)
        reach(app.buttons["explore_wangzhen"],in:app);app.buttons["explore_wangzhen"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5));shot("v3-09-wangzhen",app)
        XCTAssertFalse(app.buttons["explore_wangzhen"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_wangzhen"].isHittable)
        app.buttons["explore_qizhen"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱祁镇"))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["explore_qizhen"].isHittable)
    }
    @MainActor func chooseChild(_ id: String, in app: XCUIApplication) {
        if app.buttons["relative_" + id].exists {
            reach(app.buttons["relative_" + id],in:app);app.buttons["relative_" + id].tap()
        } else {
            reach(app.buttons["allChildren"],in:app);app.buttons["allChildren"].tap()
            reach(app.buttons["member_" + id],in:app);app.buttons["member_" + id].tap()
        }
    }
    @MainActor func openAssociates(in app: XCUIApplication) {
        reach(app.buttons["category_relationships"],in:app);app.buttons["category_relationships"].tap()
        reach(app.buttons["allAssociates"],in:app);app.buttons["allAssociates"].tap()
    }
    @MainActor func testV4OverviewAndPrinces() throws {
        let app = launch();shot("v4-01-family",app)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout:5))
        XCTAssertTrue(app.segmentedControls.firstMatch.exists)
        XCTAssertTrue(app.buttons["category_events"].exists)
        XCTAssertTrue(app.buttons["event_founding"].exists)
        shot("v4-02-person-overview",app)
        reach(app.buttons["category_relationships"],in:app)
        app.buttons["category_relationships"].tap();shot("v4-03-relationships",app)
        app.buttons["allChildren"].tap();shot("v4-04-princes",app)
        for id in ["biao","shang","gang","di","su","bai","quan"] { XCTAssertTrue(app.buttons["member_" + id].exists) }
        app.buttons["member_shang"].tap();app.buttons["personHero"].tap()
        XCTAssertFalse(app.buttons["category_remains"].exists)
        XCTAssertFalse(app.buttons["portraitEntry"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap();app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["member_bai"],in:app);app.buttons["member_bai"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱柏"));shot("v4-05-xiang-family",app)
        app.buttons["personHero"].tap();shot("v4-06-xiang-overview",app)
        XCTAssertTrue(app.buttons["category_remains"].exists)
        app.buttons["category_relationships"].tap()
        XCTAssertTrue(app.buttons["parent_yuanzhang"].isHittable)
        app.buttons["parent_yuanzhang"].tap()
        XCTAssertTrue(app.staticTexts["朱元璋"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout:5));shot("v4-07-xiang-article",app)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_events"],in:app);app.buttons["category_events"].tap();shot("v4-08-xiang-events",app)
        XCTAssertGreaterThan(app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "event_")).count, 0)
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap()
        app.buttons["personObject_v4p_xiangcenotaph"].tap();shot("v4-16-xiang-cenotaph",app)
        XCTAssertTrue(app.staticTexts["观看提示"].exists)
    }
    @MainActor func testV4CategoriesAndSources() throws {
        let app = launch();app.buttons["personHero"].tap()
        reach(app.buttons["category_events"],in:app);app.buttons["category_events"].tap()
        reach(app.buttons["event_founding"],in:app);app.buttons["event_founding"].tap()
        XCTAssertTrue(app.staticTexts["发生了什么"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        XCTAssertTrue(app.buttons["event_founding"].isHittable)
        app.terminate(); app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout:10))
        app.tabBars.buttons["家族"].tap(); XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout:10)); app.buttons["personHero"].tap()
        reach(app.buttons["category_remains"],in:app);app.buttons["category_remains"].tap();shot("v4-09-remains",app)
        app.buttons["tombCard"].tap();XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout:5))
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.navigationBars.buttons.element(boundBy:0).tap()
        reach(app.buttons["category_records"],in:app);app.buttons["category_records"].tap();shot("v4-10-records",app)
        XCTAssertTrue(app.staticTexts["年号纪年"].exists)
        app.navigationBars.buttons.element(boundBy:0).tap()
        app.swipeDown();reach(app.buttons["portraitEntry"],in:app);app.buttons["portraitEntry"].tap();shot("v4-11-portrait",app)
    }
    @MainActor func testV4LargeTypeHierarchy() throws {
        let app = launch(true);app.buttons["personHero"].tap();shot("v4-12-large-overview",app)
        reach(app.buttons["category_relationships"],in:app);shot("v4-13-large-categories",app);app.buttons["category_relationships"].tap()
        reach(app.buttons["allChildren"],in:app);app.buttons["allChildren"].tap()
        reach(app.buttons["member_bai"],in:app);shot("v4-14-large-princes",app);app.buttons["member_bai"].tap()
        app.buttons["personHero"].tap()
        reach(app.buttons["category_relationships"],in:app);app.buttons["category_relationships"].tap()
        XCTAssertTrue(app.buttons["parent_yuanzhang"].isHittable);shot("v4-15-large-parent",app)
    }

    @MainActor func testV4HistoricalPortraitLabels() throws {
        for (sequence,id,label) in [("1","yunwen","传说形象"),("6","qiyu","后世绣像"),("16","youjian","后世绘像")] {
            let app = launch();openEmperor(sequence,in:app)
            XCTAssertTrue(app.buttons["personHero"].label.contains(label))
            app.buttons["personHero"].tap()
            XCTAssertTrue(app.staticTexts[label].waitForExistence(timeout:5));shot("v4-portrait-" + id + "-overview",app)
            app.buttons["portraitEntry"].tap()
            XCTAssertTrue(app.staticTexts[label].waitForExistence(timeout:5));shot("v4-portrait-" + id + "-source",app)
            app.terminate()
        }
    }

    @MainActor func testV5DynastySelectionAndPersistence() throws {
        let app = launch(enterFamily: false)
        XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        XCTAssertTrue(app.descendants(matching: .any)["dynasty_qin"].exists)
        XCTAssertTrue(app.buttons["dynasty_qin"].exists)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap(); shot("v5-01-dynasties-qing", app)
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("努尔哈赤")); shot("v5-02-qing-family", app)
        chooseChild("q_hongtaiji", in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("皇太极"))
        app.terminate(); app.launchArguments = []; app.launch()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyPage"].waitForExistence(timeout: 10))
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14)
        XCTAssertEqual(app.buttons["dynasty_qing"].value as? String, "已选中")
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("皇太极")); shot("v5-03-qing-restored", app)
    }

    @MainActor func testV8EveryDynastyOpensAnIntroduction() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qin"], in: app, attempts: 12)
        app.buttons["dynasty_qin"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["dynastyDetail_qin"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["短暂统一与长久制度遗产"].exists)
        XCTAssertTrue(app.staticTexts["朝代总览"].exists)
        XCTAssertTrue(app.descendants(matching: .any)["territoryMap_qin"].exists)
        shot("v8-01-qin-introduction", app)
    }

    @MainActor func testV8PrehistoryMapAndSiteReading() throws {
        let app = launch(enterFamily: false)
        XCTAssertTrue(app.buttons["dynasty_prehistory"].waitForExistence(timeout: 5))
        app.buttons["dynasty_prehistory"].tap()
        app.buttons["总览"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryPage"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.descendants(matching: .any)["prehistoryMap"].exists)
        reach(app.buttons["prehistoricSite_hemudu"], in: app, attempts: 18)
        app.buttons["prehistoricSite_hemudu"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["prehistorySiteDetail_hemudu"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["发现了什么"].exists)
        XCTAssertTrue(app.staticTexts["为什么重要"].exists)
        shot("v8-02-hemudu-detail", app)
    }

    @MainActor func testV5QingSequenceArticleAndTombs() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.staticTexts["从后金兴起到帝制终结，皇位传承始终与宗室、摄政和时代转折相连。努尔哈赤与皇太极属于入关前的两代统治者。"].waitForExistence(timeout: 5))
        reach(app.buttons["succession_q_5"], in: app, attempts: 14); app.buttons["succession_q_5"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("弘历")); app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5)); app.buttons["articleEntry"].tap()
        XCTAssertTrue(app.buttons["articleContents"].waitForExistence(timeout: 5)); shot("v5-04-qianlong-article", app)
        app.tabBars.buttons["遗珍"].tap(); app.buttons["collectionCategory_tombs"].tap()
        reach(app.buttons["tomb_q_daoguang"], in: app, attempts: 16); app.buttons["tomb_q_daoguang"].tap()
        XCTAssertTrue(app.staticTexts["安葬信息"].waitForExistence(timeout: 5)); XCTAssertTrue(app.staticTexts["慕陵"].exists); shot("v5-05-muling", app)
        app.navigationBars.buttons.element(boundBy: 0).tap()
        reach(app.buttons["tomb_q_xuantong"], in: app, attempts: 16); app.buttons["tomb_q_xuantong"].tap()
        XCTAssertTrue(app.staticTexts["特殊安葬"].waitForExistence(timeout: 5)); shot("v5-06-puyi-burial", app)
    }

    @MainActor func testV5LargeTypeDynastyAndQingOverview() throws {
        let app = launch(true, enterFamily: false); shot("v5-07-large-dynasties", app)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18); app.buttons["dynasty_qing"].tap(); app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5)); app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["category_relationships"].waitForExistence(timeout: 5)); shot("v5-08-large-qing-overview", app)
    }

    @MainActor func testV5PuyiBiologicalAndRitualLineage() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_q_11"], in: app, attempts: 18); app.buttons["succession_q_11"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("溥仪"))
        XCTAssertTrue(app.buttons["relative_q_zaifeng"].label.contains("父亲"))
        XCTAssertTrue(app.buttons["relative_q_tongzhi"].label.contains("礼制承继"))
        XCTAssertTrue(app.buttons["relative_q_guangxu"].label.contains("礼制承继"))
        shot("v5-09-puyi-lineage", app)
        app.buttons["relative_q_zaifeng"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("载沣"))
        openArticle(in: app)
    }

    @MainActor func testV6TabOrderAndCategorizedMajorEvents() throws {
        let app = launch(enterFamily: false)
        XCTAssertEqual(app.tabBars.buttons.allElementsBoundByIndex.map(\.label), ["朝代", "帝序", "家族", "遗珍"])
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_0"], in: app); app.buttons["succession_0"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5)); app.buttons["personHero"].tap()
        reach(app.buttons["eventCategory_政治"], in: app)
        for category in ["政治", "军事", "文化", "经济", "社会"] {
            let tab = app.buttons["eventCategory_\(category)"]
            XCTAssertTrue(tab.exists)
            XCTAssertTrue(tab.isHittable)
        }
        app.buttons["eventCategory_军事"].tap()
        reach(app.buttons["event_join"], in: app); XCTAssertTrue(app.buttons["event_join"].isHittable)
        app.buttons["eventCategory_文化"].tap()
        reach(app.buttons["event_advice"], in: app); XCTAssertTrue(app.buttons["event_advice"].isHittable)
        app.buttons["eventCategory_经济"].tap()
        let empty = app.staticTexts["暂无条目"]
        reach(empty, in: app); XCTAssertTrue(empty.isHittable)
        reach(app.buttons["category_events"], in: app); XCTAssertTrue(app.buttons["category_events"].isHittable)
    }

    @MainActor func testV11TianqiExplosionIsSocialHistory() throws {
        let app = launch(enterFamily: false)
        openEmperor("15", in: app)
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["eventCategory_社会"].waitForExistence(timeout: 5))
        app.buttons["eventCategory_社会"].tap()
        reach(app.buttons["event_v11_wanggongchang_1626"], in: app)
        XCTAssertTrue(app.buttons["event_v11_wanggongchang_1626"].label.contains("王恭厂大爆炸"))
    }

    @MainActor func testV8KangxiSonsAndCompactHierarchy() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_qing"], in: app, attempts: 14); app.buttons["dynasty_qing"].tap()
        app.tabBars.buttons["帝序"].tap()
        reach(app.buttons["succession_q_3"], in: app, attempts: 14); app.buttons["succession_q_3"].tap()
        XCTAssertTrue(app.buttons["personHero"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["personHero"].label.contains("玄烨"))
        reach(app.buttons["allChildren"], in: app); XCTAssertTrue(app.buttons["allChildren"].label.contains("9位"))
        app.buttons["allChildren"].tap()
        for id in ["q_yinzhi_elder", "q_yinzhi_third", "q_yintang", "q_yine", "q_yinti"] {
            reach(app.buttons["member_\(id)"], in: app, attempts: 14)
            XCTAssertTrue(app.buttons["member_\(id)"].exists)
        }
        app.buttons["member_q_yinti"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("胤禵"))
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["category_relationships"].exists)
        XCTAssertTrue(app.buttons["category_records"].exists)
    }

    @MainActor func testV29ZhouTopicsOpenAsLayeredReading() throws {
        let app = launch(enterFamily: false)
        reach(app.buttons["dynasty_zhou"], in: app, attempts: 8)
        app.buttons["dynasty_zhou"].tap()
        XCTAssertTrue(app.buttons["zhouTopic_confucius"].waitForExistence(timeout: 5))
        reach(app.buttons["zhouTopic_confucius"], in: app, attempts: 10)
        app.buttons["zhouTopic_confucius"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["eraTopic_confucius"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["仁、礼与君子"].exists)
        shot("v29-zhou-confucius", app)
    }

    @MainActor func testV29ZhuDiSignatureEventsStayVisible() throws {
        let app = launch(enterFamily: false)
        openEmperor("2", in: app)
        app.buttons["personHero"].tap()
        app.buttons["eventCategory_文化"].tap()
        XCTAssertTrue(app.buttons["event_v12_zhenghe_voyages"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.buttons["event_v12_yongle_dadian"].exists)
        app.buttons["eventCategory_军事"].tap()
        XCTAssertTrue(app.buttons["event_v17_yongle_mobei"].waitForExistence(timeout: 5))
        shot("v29-zhudi-events", app)
    }

    @MainActor func testV29NarrationShowsOnlyCompactMandarinVoices() throws {
        let app = launch()
        openArticle(in: app)
        app.buttons["朗读设置"].tap()
        XCTAssertTrue(app.navigationBars["朗读设置"].waitForExistence(timeout: 5))
        let voiceButtons = app.buttons.matching(NSPredicate(format: "identifier BEGINSWITH %@", "narrationVoice_"))
        XCTAssertGreaterThanOrEqual(voiceButtons.count, 1)
        XCTAssertLessThanOrEqual(voiceButtons.count, 4)
        for rejected in ["Eddy", "Flo", "Grandma", "Grandpa", "Reed", "Rocko", "Sandy", "Shelley"] {
            XCTAssertFalse(app.staticTexts[rejected].exists)
        }
        for index in 0..<voiceButtons.count {
            XCTAssertFalse(voiceButtons.element(boundBy: index).identifier.lowercased().contains("siri"))
        }
        shot("v29-narration-voices", app)
    }

    @MainActor func testV33ThoughtCollectionAndFreshFamilyTab() throws {
        let app = launch(enterFamily: false)
        app.tabBars.buttons["遗珍"].tap()
        XCTAssertTrue(app.buttons["collectionCategory_ideas"].waitForExistence(timeout: 5))
        app.buttons["collectionCategory_ideas"].tap()
        XCTAssertTrue(app.buttons["artifact_idea_wang_yangming"].waitForExistence(timeout: 5))
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱元璋"))
        chooseChild("di", in: app)
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱棣"))
        app.tabBars.buttons["朝代"].tap()
        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["personHero"].label.contains("朱元璋"))
    }

    @MainActor func testV33PersonOverviewVisual() throws {
        let app = launch()
        app.buttons["personHero"].tap()
        XCTAssertTrue(app.buttons["articleEntry"].waitForExistence(timeout: 5))
        shot("v33-person-overview", app)
    }

    @MainActor func testV34ExpandedFamilyAndQingSuccessionLanguage() throws {
        let app = launch()
        XCTAssertTrue(app.buttons["relative_di"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["祖先"].exists)
        XCTAssertTrue(app.staticTexts["子女"].exists)
        shot("v34-expanded-family", app)

        app.tabBars.buttons["朝代"].tap()
        reach(app.buttons["dynasty_qing"], in: app, attempts: 18)
        app.buttons["dynasty_qing"].tap()
        XCTAssertTrue(app.navigationBars.firstMatch.waitForExistence(timeout: 5))
        app.navigationBars.buttons.element(boundBy: 0).tap()
        shot("v34-dynasty-selection", app)

        app.tabBars.buttons["家族"].tap()
        XCTAssertTrue(app.buttons["relative_q_taksi"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["第8子"].exists)
        XCTAssertTrue(app.staticTexts["第14子"].exists)
        shot("v35-qing-expanded-lineage", app)

        app.tabBars.buttons["帝序"].tap()
        XCTAssertTrue(app.descendants(matching: .any)["successionPage_qing"].waitForExistence(timeout: 5))
        XCTAssertTrue(app.staticTexts["开创后金"].exists)
        XCTAssertTrue(app.staticTexts["父子相承"].exists)
        shot("v34-qing-succession", app)
    }

}
