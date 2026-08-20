import json
from pathlib import Path

from django.core.management.base import BaseCommand

from exercises.models import Exercise


class Command(BaseCommand):

    help = 'Import exercises from exercises.json'

    def handle(self, *args, **options):

        file_path = (
            Path.cwd()
            / 'data'
            / 'exercises.json'
        )

        if not file_path.exists():

            self.stdout.write(
                self.style.ERROR(
                    f'File not found: {file_path}'
                )
            )

            return

        self.stdout.write(
            'Loading exercises.json...'
        )

        try:

            with open(
                file_path,
                'r',
                encoding='utf-8'
            ) as file:

                exercises = json.load(file)

        except json.JSONDecodeError as e:

            self.stdout.write(
                self.style.ERROR(
                    f'Invalid JSON file: {e}'
                )
            )

            return

        created_count = 0
        updated_count = 0

        for item in exercises:

            exercise, created = Exercise.objects.update_or_create(

                external_id=item['id'],

                defaults={

                    'name': item['name'],

                    'slug': f"exercise-{item['id']}",

                    'category': item.get(
                        'category',
                        ''
                    ),

                    'body_part': item.get(
                        'body_part',
                        ''
                    ),

                    'equipment': item.get(
                        'equipment',
                        ''
                    ),

                    'target_muscle': item.get(
                        'target',
                        ''
                    ),

                    'muscle_group': item.get(
                        'muscle_group',
                        ''
                    ),

                    'secondary_muscles': item.get(
                        'secondary_muscles',
                        []
                    ),

                    'instructions': item.get(
                        'instructions',
                        {}
                    ),

                    'instruction_steps': item.get(
                        'instruction_steps',
                        {}
                    ),

                    'media_id': item.get(
                        'media_id',
                        ''
                    ),

                    'image': item.get(
                        'image',
                        ''
                    ),

                    'gif_url': item.get(
                        'gif_url',
                        ''
                    ),

                    'attribution': item.get(
                        'attribution',
                        ''
                    ),
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                'Import completed!'
            )
        )

        self.stdout.write(
            f'Created: {created_count}'
        )

        self.stdout.write(
            f'Updated: {updated_count}'
        )

        self.stdout.write(
            f'Total: {len(exercises)}'
        )