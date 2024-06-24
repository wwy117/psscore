import argparse
import csv
import logging

MATCH_FEE = 30
USPSA_CLASSIFIER_FEE = 3
NW_SESSION_FEE = 1

def discount(record: dict[str, str], match_fee: float) -> int:
    if record['Setup']:
        return match_fee
    if record['RO']:
        return 10
    if record['Active Military']:
        return 10
    if record['Junior']:
        return 10
    if record['Renton Member']:
        return 5
    return 0

def main(filepath: str, match_fee: float, uspsa: bool):
    # Note that the csv file need to have two columns: RO and Setup
    # The RO column represents a working RO, and Setup column represents a setup crew.
    shooters = []
    headers = []
    uspsa_fee = USPSA_CLASSIFIER_FEE if uspsa else 0
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if not headers:
                headers = row
                continue
            shooter = {}
            for i in range(len(headers)):
                try:
                    shooter[headers[i]] = row[i]
                except IndexError:
                    logging.warning(f'{i} is out of boundary of {row}\n')
            shooters.append(shooter)

    # Sanity check on errors
    if len(shooters) == 0:
        raise RuntimeError('The shooter list is empty')
    shooter = shooters[0]
    if not 'RO' in shooter:
        raise RuntimeError('Missing RO column')
    if not 'Setup' in shooter:
        raise RuntimeError('Missing Setup column')
    if '"Paid Status"' in shooter:
        raise RuntimeError('Double quoted field name presents. Open the doc in excel, save it as csv and rerun this program again.')

    # Process data & generate lists
    paid_count = 0
    renton_members = []
    active_militarys = []
    juniors = []
    setup_crews = []
    ROs = []
    total_revenue = 0
    total_discount = 0
    refund_list = []
    uspsa_members = []
    staff_count = 0
    for s in shooters:
        if s['Paid Status'] != 'Paid':
            continue
        if 'Staff' in s['Approval Status']:
            staff_count += 1
            if s['Member Number']:
                uspsa_members.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
            continue
        paid_count += 1
        total_revenue += match_fee
        if s['RO']:
            ROs.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        if s['Setup']:
            setup_crews.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        if s['Active Military']:
            active_militarys.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        if s['Renton Member']:
            renton_members.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        if s['Junior']:
            juniors.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        if s['Member Number']:
            uspsa_members.append({'First Name': s['First Name'], 'Last Name': s['Last Name']})
        shooter_discount = discount(s, match_fee)
        if shooter_discount:
            refund_list.append(({'First Name': s['First Name'], 'Last Name': s['Last Name'],
                                 'Refund': str(shooter_discount)}))
        total_discount += shooter_discount

    # Print reports
    logging.info(f'Gross revenue: {total_revenue}')
    logging.info(f'Total discount: {total_discount}')
    logging.info(f'Total USPSA fee: {len(uspsa_members) * uspsa_fee}')
    logging.info(f'Total NW Session fee: {(paid_count + staff_count) * NW_SESSION_FEE}')
    logging.info(f'Net Revenue: {total_revenue - total_discount - len(uspsa_members) * uspsa_fee - paid_count * NW_SESSION_FEE}')
    logging.info(f'Total Paid Shooters: {paid_count}')
    logging.info(f'Number of setup crew: {len(setup_crews)}')
    logging.info(f'Number of ROs: {len(ROs)}')
    logging.info(f'Number of Active Military: {len(active_militarys)}')
    logging.info(f'Number of Junior: {len(juniors)}')
    logging.info(f'Number of Renton Member: {len(renton_members)}')
    logging.info(f'Number of USPSA members: {len(uspsa_members)}')
    logging.info('Refund list:')
    for s in refund_list:
        logging.info(f'{s}')
    logging.info('Setup Crew list:')
    for s in setup_crews:
        logging.info(f'{s}')
    logging.info('RO list:')
    for s in ROs:
        logging.info(f'{s}')
    logging.info('Renton Member list:')
    for s in renton_members:
        logging.info(f'{s}')
    logging.info('Active Military list:')
    for s in active_militarys:
        logging.info(f'{s}')
    logging.info('Junior list:')
    for s in juniors:
        logging.info(f'{s}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--filepath', type = str, help = 'file to open')
    parser.add_argument('--fee', type = float, default = 30.0, help = 'the fee per person')
    parser.add_argument('--uspsa', action=argparse.BooleanOptionalAction, default=True, help = 'whether to pay USPSA.org or not')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    main(args.filepath, args.fee, args.uspsa)
