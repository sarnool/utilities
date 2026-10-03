"""HTML and CSS cleanup helpers."""

from __future__ import annotations

import os
import re
from typing import List

import cssutils
import logging
from bs4 import BeautifulSoup, Tag

cssutils.log.setLevel(logging.CRITICAL)


def extract_main_quiz_content(soup, target_class):
    try:
        extracted_content = soup.find("div", class_=target_class)
        if not extracted_content:
            print(f"Error: No div with class '{target_class}' found in the file.")
            return soup

        if soup.body:
            soup.body.clear()
            soup.body.append(extracted_content)
        else:
            print("Error: The file does not contain a standard <body> tag to modify.")
            return soup
        return soup
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


def process_html_content(soup, target_tag, target_class, action):
    is_updated = False
    target_elements: List[Tag] = soup.find_all(target_tag, class_=target_class)

    if target_elements:
        if action == "drop":
            for target_element in target_elements:
                target_element.decompose()
            is_updated = True

    return soup


def find_and_replace(original_content, search_text, replace_text):
    original_content = original_content.replace("\r\n", "\n")
    escaped_text = re.escape(search_text).replace("\\ ", r"\s*").replace("\\\n", r"\s*")
    return re.sub(escaped_text, replace_text, original_content)


def process_css_content(sheet, target_selector, target_property, new_style_value):
    for rule in sheet.cssRules:
        if rule.type == rule.STYLE_RULE:
            if target_selector.lower() in rule.selectorText.lower():
                rule.style.setProperty(target_property, new_style_value, priority="")
    return sheet


def replace_in_files_wrapper(dir_str: str, actions: list, main_quiz_class_name: str,
                             search_replace_list_cleanup: list, update_css_list_cleanup: list,
                             update_html_list_cleanup: list,
                             search_replace_list_remove_answers: list, update_css_list_remove_answers: list,
                             update_html_list_remove_answers: list):
    print(f"--- Starting file replacement in '{os.path.abspath(dir_str)}' ---")

    for dirpath, _, filenames in os.walk(dir_str):
        if any(exclude in dirpath for exclude in [".git", "__pycache__", "node_modules"]):
            continue

        for filename in filenames:
            if not filename.endswith((".txt", ".py", ".html", ".css", ".js", ".md")):
                continue

            file_extn = filename.split(".")[-1]
            filepath = os.path.join(dirpath, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                original_content = f.read()

            new_content = original_content

            for action in actions:
                if action == "remove_answers":
                    use_list = search_replace_list_remove_answers
                elif action == "cleanup":
                    use_list = search_replace_list_cleanup
                else:
                    use_list = []

                for item in use_list:
                    new_content = find_and_replace(new_content, item["search"], item["replace"])

            if file_extn == "css":
                for action in actions:
                    use_list = update_css_list_remove_answers if action == "remove_answers" else update_css_list_cleanup if action == "cleanup" else []
                    sheet = None
                    for item in use_list:
                        target_selector = item["target_selector"]
                        if target_selector in new_content:
                            if sheet is None:
                                sheet = cssutils.parseString(new_content)
                            target_property = item["target_property"]
                            new_style_value = item["new_style_value"]
                            sheet = process_css_content(sheet, target_selector, target_property, new_style_value)
                    if sheet is not None:
                        new_content = sheet.cssText.decode("utf-8")

            if file_extn in ["html", "htm"]:
                soup = BeautifulSoup(new_content, "lxml")
                if "cleanup" in actions:
                    soup = extract_main_quiz_content(soup, main_quiz_class_name)

                for action in actions:
                    use_list = update_html_list_remove_answers if action == "remove_answers" else update_html_list_cleanup if action == "cleanup" else []
                    for item in use_list:
                        target_tag = item["target_tag"]
                        target_class = item["target_class"]
                        action_value = item["action"]
                        soup = process_html_content(soup, target_tag, target_class, action_value)

                new_content = str(soup.prettify())

            if new_content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)

    return True


def main():
    print("HTML/CSS cleanup utility")


if __name__ == "__main__":
    main()
