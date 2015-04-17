from venn_email import VennEmail


def main():
    v = VennEmail()
    success, sent_with = v.send(from_='foo@example.com', to='bar@example.com.com', subject='my subject', body='my body')
    if success:
        print 'succeeded with {}'.format(sent_with)
    else:
        print 'all failed'


if __name__ == '__main__':
    main()
