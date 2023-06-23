from flask import Flask, jsonify, request
import csv
import traceback

app = Flask(__name__)

def read_csv_file():
    data = []
    with open('data.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data


#http://localhost:5000/api/total_items?start_date=2022-07-01&end_date=2023-09-30&department=Marketting
@app.route('/api/total_items', methods=['GET'])
def get_total_items():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')

        # Assuming the date format is YYYY-MM-DD in the CSV file
        q3_start = start_date[:7] + '-07-01'
        q3_end = end_date[:7] + '-09-30'

        data = read_csv_file()

        total_items = 0
        for row in data:
            row_date = row['date'][:10]  # Extract date from the 'date' field
            if (
                q3_start <= row_date <= q3_end and
                row['department'] == department
            ):
                total_items += int(row['seats'])

        return jsonify(total_items)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred.'}), 500


#http://localhost:5000/api/nth_most_total_item?item_by=price&start_date=2022-04-01&end_date=2022-06-30&n=4        
@app.route('/api/nth_most_total_item', methods=['GET'])
def get_nth_most_total_item():
    try:
        item_by = request.args.get('item_by')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        n = int(request.args.get('n'))

        # Assuming the date format is YYYY-MM-DD in the CSV file
        q_start = start_date[:7] + '-01-01'
        q_end = end_date[:7] + '-12-31'

        data = read_csv_file()

        items = []
        for row in data:
            row_date = row['date'][:10]  # Extract date from the 'date' field
            if (
                q_start <= row_date <= q_end
            ):
                items.append(row)

        if item_by == 'quantity':
            items.sort(key=lambda x: int(x['seats']), reverse=True)
        elif item_by == 'price':
            items.sort(key=lambda x: float(x['amount']), reverse=True)
        else:
            return jsonify({'error': 'Invalid value for item_by parameter. Must be "quantity" or "price".'}), 400

        if n > len(items):
            return jsonify({'error': 'Value of n exceeds the number of items available.'}), 400

        nth_most_item = items[n-1]

        if item_by == 'quantity':
            return jsonify(nth_most_item['software'])
        else:
            return jsonify(nth_most_item['user'])

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred.'}), 500


#http://localhost:5000/api/percentage_of_department_wise_sold_items?start_date=2022-01-01&end_date=2022-12-31
@app.route('/api/percentage_of_department_wise_sold_items', methods=['GET'])
def get_percentage_of_department_wise_sold_items():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Assuming the date format is YYYY-MM-DD in the CSV file
        q_start = start_date[:7] + '-01-01'
        q_end = end_date[:7] + '-12-31'

        data = read_csv_file()

        department_counts = {}
        total_items = 0

        for row in data:
            row_date = row['date'][:10]  # Extract date from the 'date' field
            if (
                q_start <= row_date <= q_end
            ):
                department = row['department']
                seats = int(row['seats'])
                total_items += seats
                if department in department_counts:
                    department_counts[department] += seats
                else:
                    department_counts[department] = seats

        department_percentages = {}

        for department, count in department_counts.items():
            percentage = (count / total_items) * 100
            department_percentages[department] = round(percentage, 2)

        return jsonify(department_percentages)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred.'}), 500


#http://localhost:5000/api/monthly_sales?product=Outplay&year=2022


@app.route('/api/monthly_sales', methods=['GET'])
def get_monthly_sales():
    try:
        product = request.args.get('product')
        year = int(request.args.get('year'))

        data = read_csv_file()

        monthly_sales = [0] * 12

        for row in data:
            row_date = row['date']
            row_product = row['software']
            if row_product == product:
                row_year = int(row_date[:4])
                row_month = int(row_date[5:7])
                if row_year == year:
                    monthly_sales[row_month - 1] += float(row['amount'])

        return jsonify(monthly_sales)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred.'}), 500




if __name__ == '__main__':
    app.run()
