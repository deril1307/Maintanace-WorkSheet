import json
from app import app, db
from models import User, MwsPart, MwsStep  # Jangan impor Tittle karena sudah tidak dipakai

def seed_data():
    with app.app_context():
        print("Memulai proses seeding data MWS...")

        # 1. Baca file JSON
        try:
            with open('worksheet_data.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("Error: File 'worksheet_data.json' tidak ditemukan.")
            return
        except json.JSONDecodeError:
            print("Error: File JSON rusak atau tidak valid.")
            return

        parts_data = data.get('parts', {})
        if not parts_data:
            print("Tidak ada data 'parts' dalam JSON.")
            return
        
        print(f"\nMemproses {len(parts_data)} MWS dari JSON...")

        for mws_id_str, mws_data in parts_data.items():
            part_number = mws_data.get('partNumber')
            existing_part = MwsPart.query.filter_by(part_number=part_number).first()
            if existing_part:
                print(f"MWS Part '{part_number}' sudah ada di database, dilewati.")
                continue

            # Ambil assigned user
            assigned_user = User.query.filter_by(nik=mws_data.get('assignedTo')).first()

            # Ambil tittle dan job_type dari JSON langsung (bukan object lagi)
            tittle_value = mws_data.get('tittle', '')
            job_type_value = mws_data.get('jobType', '')

            # Buat MwsPart baru
            new_mws_part = MwsPart(
                part_number=part_number,
                serial_number=mws_data.get('serialNumber'),
                ref=mws_data.get('ref'),
                customer=mws_data.get('customer'),
                ac_type=mws_data.get('acType'),
                wbs_no=mws_data.get('wbsNo'),
                worksheet_no=mws_data.get('worksheetNo'),
                iwo_no=mws_data.get('iwoNo'),
                shop_area=mws_data.get('shopArea'),
                revision=mws_data.get('revision'),
                status=mws_data.get('status'),
                current_step=mws_data.get('currentStep'),
                target_date=mws_data.get('targetDate'),
                start_date=mws_data.get('startDate') or None,
                finish_date=mws_data.get('finishDate') or None,
                tittle=tittle_value,
                job_type=job_type_value,
                assigned_to_id=assigned_user.id if assigned_user else None
            )
            db.session.add(new_mws_part)
            db.session.commit()
            print(f"-> MWS Part '{new_mws_part.part_number}' berhasil ditambahkan.")

            # Tambah steps
            steps_data = mws_data.get('steps', [])
            for step_data in steps_data:
                completed_by_user = User.query.filter_by(nik=step_data.get('completedBy')).first()
                new_step = MwsStep(
                    mws_part_id=new_mws_part.id,
                    step_number=step_data.get('no'),
                    description=step_data.get('description'),
                    details=step_data.get('details'),
                    status=step_data.get('status'),
                    man=step_data.get('man'),
                    hours=step_data.get('hours'),
                    tech=step_data.get('tech'),
                    insp=step_data.get('insp'),
                    completed_date=step_data.get('completedDate') or None,
                    completed_by_id=completed_by_user.id if completed_by_user else None
                )
                db.session.add(new_step)

            db.session.commit()
            print(f"--> {len(steps_data)} step untuk '{new_mws_part.part_number}' berhasil ditambahkan.")

        print("\n✅ Proses seeding selesai!")

if __name__ == '__main__':
    seed_data()
