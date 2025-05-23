import os
import subprocess
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def backup_database():
    """Backup the MySQL database to a SQL file"""
    # Get database configuration from environment variables
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'flight_booking')
    }
    
    # Create backups directory if it doesn't exist
    backup_dir = 'database_backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"{db_config['database']}_backup_{timestamp}.sql")
    
    # Build the mysqldump command
    cmd = [
        'mysqldump',
        f'--host={db_config["host"]}',
        f'--user={db_config["user"]}',
        f'--password={db_config["password"]}',
        '--single-transaction',
        '--routines',
        '--triggers',
        '--events',
        db_config['database']
    ]
    
    try:
        print(f"Backing up database '{db_config['database']}' to {backup_file}...")
        
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        print(f"Backup completed successfully: {backup_file}")
        return backup_file
        
    except subprocess.CalledProcessError as e:
        print(f"Error backing up database: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def list_backups():
    """List all available database backups"""
    backup_dir = 'database_backups'
    if not os.path.exists(backup_dir):
        print("No backups found.")
        return []
    
    backups = []
    for filename in sorted(os.listdir(backup_dir), reverse=True):
        if filename.endswith('.sql'):
            filepath = os.path.join(backup_dir, filename)
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # Size in MB
            backups.append({
                'filename': filename,
                'path': filepath,
                'size_mb': round(file_size, 2),
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            })
    
    if not backups:
        print("No backup files found.")
    else:
        print("\nAvailable Backups:")
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['filename']} ({backup['size_mb']} MB, {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')})")
    
    return backups

def restore_database(backup_file):
    """Restore the database from a backup file"""
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        return False
    
    # Get database configuration from environment variables
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'flight_booking')
    }
    
    # Build the mysql command
    cmd = [
        'mysql',
        f'--host={db_config["host"]}',
        f'--user={db_config["user"]}',
        f'--password={db_config["password"]}',
        db_config['database']
    ]
    
    try:
        print(f"Restoring database from {backup_file}...")
        
        with open(backup_file, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        
        print("Database restored successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error restoring database: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    """Main function for the backup utility"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup and Restore Utility')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a new database backup')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from a backup')
    restore_parser.add_argument('backup_file', nargs='?', help='Path to the backup file to restore')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_database()
    elif args.command == 'list':
        list_backups()
    elif args.command == 'restore':
        if args.backup_file:
            restore_database(args.backup_file)
        else:
            # Show interactive restore menu
            backups = list_backups()
            if backups:
                try:
                    choice = int(input("\nEnter the number of the backup to restore (or 0 to cancel): "))
                    if 1 <= choice <= len(backups):
                        confirm = input(f"Are you sure you want to restore from {backups[choice-1]['filename']}? This will overwrite the current database. (y/n): ")
                        if confirm.lower() == 'y':
                            restore_database(backups[choice-1]['path'])
                    elif choice != 0:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
