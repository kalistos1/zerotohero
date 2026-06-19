from django.core.management.base import BaseCommand
from core.models import SponsorshipTier

class Command(BaseCommand):
    help = 'Seeds initial Sponsorship Tier data from the 2026 PDF.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Sponsorship Tiers...')
        
        tiers = [
            {
                'name': 'Bronze',
                'price_display': '₦150,000 (~$90)',
                'description': 'A credibility and goodwill play. Visibly associated with real graduates across Africa.',
                'features': 'Logo on website & certificates\nBrand tagged in 24 sponsor posts\nMention in final impact report\nDocumented reach data',
                'is_recommended': False,
                'icon_class': 'fas fa-medal',
                'bg_class': 'bronze-bg',
                'order': 1
            },
            {
                'name': 'Silver',
                'price_display': '₦350,000 (~$210)',
                'description': 'Direct pipeline access. The talent access alone is worth the investment.',
                'features': 'Everything in Bronze\nLogo on all class slides & banners\nOne guest speaker slot\nPriority access to graduate talent',
                'is_recommended': True,
                'icon_class': 'fas fa-gem',
                'bg_class': 'silver-bg',
                'order': 2
            },
            {
                'name': 'Gold',
                'price_display': '₦750,000 (~$450)',
                'description': 'First-pick access to top graduates. A real competitive advantage in hiring.',
                'features': 'Everything in Silver\nCo-branded certificates to all\n5 dedicated promotional posts\nFirst-pick access to top 10 graduates',
                'is_recommended': False,
                'icon_class': 'fas fa-crown',
                'bg_class': 'gold-bg',
                'order': 3
            },
            {
                'name': 'Platinum',
                'price_display': '₦1,500,000 (~$900)',
                'description': 'Consistent, documented brand presence inside a growing developer community.',
                'features': 'Everything in Gold\nTitle Sponsor status\nHomepage branding from launch\nSpeaking slots at ceremonies',
                'is_recommended': False,
                'icon_class': 'fas fa-rocket',
                'bg_class': 'platinum-bg',
                'order': 4
            },
            {
                'name': 'In-Kind',
                'price_display': 'Actively Welcomed',
                'description': 'We welcome cloud credits, domain hosting, communication tools, and developer subscriptions.',
                'features': 'AWS, GCP, Azure Credits\nZoom, Google Workspace\nJetBrains, GitHub Pro, Coursera',
                'is_recommended': False,
                'icon_class': 'fas fa-handshake',
                'bg_class': 'inkind-bg',
                'order': 5
            }
        ]

        created_count = 0
        for tier_data in tiers:
            tier, created = SponsorshipTier.objects.update_or_create(
                name=tier_data['name'],
                defaults=tier_data
            )
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new Sponsorship Tiers.'))
