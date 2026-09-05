import SwiftUI
import MapKit

/// Native annotation collision handling keeps nearby site labels readable.
struct PrehistoryMap: UIViewRepresentable {
    let sites: [PrehistorySite]
    var resetToken: String = "overview"
    let openSite: (String) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(openSite: openSite) }
    func makeUIView(context: Context) -> MKMapView {
        let map = MKMapView()
        map.delegate = context.coordinator
        map.pointOfInterestFilter = .excludingAll
        map.isRotateEnabled = false
        map.isPitchEnabled = false
        let configuration = MKStandardMapConfiguration(elevationStyle: .flat, emphasisStyle: .muted)
        configuration.pointOfInterestFilter = .excludingAll
        map.preferredConfiguration = configuration
        map.setRegion(MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 34.5, longitude: 110), span: MKCoordinateSpan(latitudeDelta: 30, longitudeDelta: 43)), animated: false)
        context.coordinator.resetToken = resetToken
        map.addAnnotations(sites.map(SiteAnnotation.init))
        return map
    }
    func updateUIView(_ map: MKMapView, context: Context) {
        context.coordinator.openSite = openSite
        let current = map.annotations.compactMap { $0 as? SiteAnnotation }
        let ids = Set(sites.map(\.id))
        let currentIDs = Set(current.map(\.siteID))
        map.removeAnnotations(current.filter { !ids.contains($0.siteID) })
        map.addAnnotations(sites.filter { !currentIDs.contains($0.id) }.map(SiteAnnotation.init))
        if context.coordinator.resetToken != resetToken {
            context.coordinator.resetToken = resetToken
            map.setRegion(MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 34.5, longitude: 110), span: MKCoordinateSpan(latitudeDelta: 30, longitudeDelta: 43)), animated: !UIAccessibility.isReduceMotionEnabled)
        }
    }

    final class SiteAnnotation: NSObject, MKAnnotation {
        let siteID: String
        let title: String?
        let coordinate: CLLocationCoordinate2D
        init(_ site: PrehistorySite) {
            siteID = site.id; title = site.name
            coordinate = CLLocationCoordinate2D(latitude: site.latitude, longitude: site.longitude)
        }
    }
    final class Coordinator: NSObject, MKMapViewDelegate {
        var resetToken = "overview"
        var openSite: (String) -> Void
        init(openSite: @escaping (String) -> Void) { self.openSite = openSite }
        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            let view = MKAnnotationView(annotation: annotation, reuseIdentifier: nil)
            let label = UILabel()
            label.font = .preferredFont(forTextStyle: .caption1)
            label.textColor = UIColor(Theme.ink)
            if let cluster = annotation as? MKClusterAnnotation {
                let members = cluster.memberAnnotations.compactMap { $0 as? SiteAnnotation }.sorted { $0.siteID < $1.siteID }
                label.text = "\(members.first?.title ?? "遗址")等\(members.count)处"
                view.accessibilityIdentifier = "siteCluster_" + members.map(\.siteID).joined(separator: "_")
                view.accessibilityLabel = label.text! + "，点按展开"
            } else if let site = annotation as? SiteAnnotation {
                label.text = site.title
                view.clusteringIdentifier = "prehistoricSites"
                view.accessibilityIdentifier = "siteMarker_" + site.siteID
                view.accessibilityLabel = (site.title ?? "遗址") + "，查看详情"
            } else { return nil }
            label.sizeToFit()
            view.frame = CGRect(x: 0, y: 0, width: label.frame.width + 16, height: 44)
            view.backgroundColor = UIColor(Theme.paper).withAlphaComponent(0.97)
            view.layer.cornerRadius = 6
            view.centerOffset = CGPoint(x: 0, y: -16)
            label.frame.origin = CGPoint(x: 8, y: 4)
            view.addSubview(label)
            let dot = UIView(frame: CGRect(x: view.bounds.midX - 3, y: 35, width: 6, height: 6))
            dot.backgroundColor = UIColor(Theme.cinnabar); dot.layer.cornerRadius = 3
            view.addSubview(dot)
            view.collisionMode = .rectangle
            view.displayPriority = annotation is MKClusterAnnotation ? .defaultHigh : .defaultLow
            view.isAccessibilityElement = true
            view.accessibilityTraits = .button
            return view
        }
        func mapView(_ mapView: MKMapView, didAdd views: [MKAnnotationView]) {
            guard !UIAccessibility.isReduceMotionEnabled else { return }
            for view in views {
                view.alpha = 0
                UIView.animate(withDuration: 0.2) { view.alpha = 1 }
            }
        }
        func mapView(_ mapView: MKMapView, didSelect view: MKAnnotationView) {
            guard let annotation = view.annotation else { return }
            mapView.deselectAnnotation(annotation, animated: false)
            if let cluster = annotation as? MKClusterAnnotation {
                let bounds = cluster.memberAnnotations.reduce(MKMapRect.null) { rect, member in
                    let point = MKMapPoint(member.coordinate)
                    return rect.union(MKMapRect(x: point.x, y: point.y, width: 1, height: 1))
                }
                mapView.setVisibleMapRect(bounds, edgePadding: UIEdgeInsets(top: 62, left: 88, bottom: 50, right: 88), animated: !UIAccessibility.isReduceMotionEnabled)
            } else if let site = annotation as? SiteAnnotation {
                openSite(site.siteID)
            }
        }
    }
}
