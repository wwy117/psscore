import argparse
import csv

MATCH_FEE = 30
USPSA_CLASSIFIER_FEE = 3
NW_SESSION_FEE = 1

def discount(record: dict[str, str]) -> int:
    if record['Setup']:
        return MATCH_FEE
    if record['RO']:
        return 10
    if record['Active Military']:
        return 10
    if record['Junior']:
        return 10
    if record['Renton Member']:
        return 5
    return 0

def main(filepath: str):
    # Note that the csv file need to have two columns: RO and Setup
    # The RO column represents a working RO, and Setup column represents a setup crew.
    shooters = []
    headers = []
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
                    print(f'{i} is out of boundary of {row}\n')
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
        total_revenue += MATCH_FEE
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
        shooter_discount = discount(s)
        if shooter_discount:
            refund_list.append(({'First Name': s['First Name'], 'Last Name': s['Last Name'],
                                 'Refund': str(shooter_discount)}))
        total_discount += shooter_discount

    # Print reports
    print(f'Gross revenue: {total_revenue}')
    print(f'Total discount: {total_discount}')
    print(f'Total USPSA fee: {len(uspsa_members) * USPSA_CLASSIFIER_FEE}')
    print(f'Total NW Session fee: {(paid_count + staff_count) * NW_SESSION_FEE}')
    print(f'Net Revenue: {total_revenue - total_discount - len(uspsa_members) * USPSA_CLASSIFIER_FEE - paid_count * NW_SESSION_FEE}')
    print(f'Total Paid Shooters: {paid_count}')
    print(f'Number of setup crew: {len(setup_crews)}')
    print(f'Number of ROs: {len(ROs)}')
    print(f'Number of Active Military: {len(active_militarys)}')
    print(f'Number of Junior: {len(juniors)}')
    print(f'Number of Renton Member: {len(renton_members)}')
    print(f'Number of USPSA members: {len(uspsa_members)}')
    print('Refund list:')
    for s in refund_list:
        print(f'{s}')
    print('Setup Crew list:')
    for s in setup_crews:
        print(f'{s}')
    print('RO list:')
    for s in ROs:
        print(f'{s}')
    print('Renton Member list:')
    for s in renton_members:
        print(f'{s}')
    print('Active Military list:')
    for s in active_militarys:
        print(f'{s}')
    print('Junior list:')
    for s in juniors:
        print(f'{s}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--filepath', type = str, help = 'file to open')
    args = parser.parse_args()
    main(args.filepath)

