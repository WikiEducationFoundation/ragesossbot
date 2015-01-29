#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to read a list of course pages (based on course ID) and then
create the /sandbox subpage for any enrolled students if their sandbox
does not already exist.
"""
#
# (C) Pywikibot team, 2006-2014
# (C) Sage Ross, 2014-2015
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 9c315ea1c38f5f9f2d74a4e8929403ffa35b2987 $'
#

import pywikibot
import string
import urllib, urllib2, json
from pywikibot import pagegenerators
from pywikibot import i18n

# Configuration variables
COURSES_LIST = u"Wikipedia:Education_program/Dashboard/course_ids"
CONTENTS = '{{student sandbox}}'

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class BasicBot:

    """An incomplete sample bot."""

    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, dry):
        """
        Constructor.

        Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
            @param dry: If True, doesn't do any real changes, but only shows
                        what would have been changed.
            @type dry: boolean.
        """
        self.generator = generator
        self.dry = dry

        # Set the edit summary message
        site = pywikibot.Site()
        self.summary = 'adding ' + CONTENTS
        # Set the control page, which is used to turn the bot on and off. The page text should simply be 'run' to turn it on.
        controlpage = pywikibot.Page(site, u"User:RagesossBot/control")
        self.control = controlpage.get()

    def getsandboxes(self):
        # write a file with course page IDs
        site = pywikibot.Site()
        course_ids_page = pywikibot.Page(site, COURSES_LIST)
        course_ids = self.load(course_ids_page)
        course_ids = course_ids.splitlines()
        
        # get list of users in all these courses
        users = []
        for course_id in course_ids:
            api_query_url = "http://en.wikipedia.org/w/api.php?action=liststudents&format=json&courseids=" + course_id
            response = urllib2.urlopen(api_query_url)
            str_response = response.read()
            data = json.loads(str_response, "utf8" )
            users_data = data["students"]
            for user in users_data:
                users.append(user["username"])
        
        # turn these usernames into /sandbox user pages    
        users = [('User:' + user + '/sandbox') for user in users]
        f = open('studentsandboxes.txt', 'w')
        for user in users:
	    user = unicode(user).encode('utf8')
            f.write(user)
            f.write('\n')
        f.close()
        
    def run(self):
	# If the text of the control page is not simply 'run', do not do anything.
        if self.control == 'run':
            for page in self.generator:
                self.treat(page)
        else:
            print 'Control text not found. Stopping the bot.'
 
    def treat(self, page):
        """ Load the given page, does some changes, and saves it. """
        text = self.load(page)
        if not text=='blank page':
            return
 
        ################################################################
        # NOTE: Here you can modify the text in whatever way you want. #
        ################################################################
 
        # If you find out that you do not want to edit this page, just return.
        # Example: This puts the text 'Test' at the beginning of the page.
        text = CONTENTS
 
        if not self.save(text, page, self.summary):
            pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))
 
    def load(self, page):
        """ Load the text of the given page. """
        try:
            # Load the page
            text = page.get()
        except pywikibot.exceptions.NoPage:
            # This bot only works on blank pages, so we want 'load' to tell us
            # when that's the case.
            pywikibot.output(u"Page %s doesn't exist, so let's create it."
                             % page.title(asLink=True))

            return 'blank page'
            
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None
 
    def save(self, text, page, comment=None, minorEdit=True,
             botflag=True):
        """ Update the given page with new text. """
        # only save if something was changed
        if True:
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            # pywikibot.showDiff(page.get(), text)
            pywikibot.output(u'Comment: %s' % comment)
            if not self.dry:
                if True:
                    try:
                        page.text = text
                        # Save the page
                        page.save(comment=comment or self.comment,
                                  minor=minorEdit, botflag=botflag)
                    except pywikibot.LockedPage:
                        pywikibot.output(u"Page %s is locked; skipping."
                                         % page.title(asLink=True))
                    except pywikibot.EditConflict:
                        pywikibot.output(
                            u'Skipping %s because of edit conflict'
                            % (page.title()))
                    except pywikibot.SpamfilterError as error:
                        pywikibot.output(
                            u'Cannot change %s because of spam blacklist entry %s'
                            % (page.title(), error.url))
                    else:
                        return True
        return False

def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    # Process global arguments to determine desired site
    local_args = pywikibot.handle_args(args)

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # If dry is True, doesn't do any real changes, but only show
    # what would have been changed.
    dry = False

    sandboxbot = BasicBot(gen, dry)
    # Get the list of sandboxes
    sandboxbot.getsandboxes()

    # load the sanboxes as a list of pages
    genFactory.handleArg("-file:studentsandboxes.txt")

    gen = genFactory.getCombinedGenerator()
        
    gen = pagegenerators.PreloadingGenerator(gen)
    bot = BasicBot(gen, dry)
    bot.run()

if __name__ == "__main__":
    main()
